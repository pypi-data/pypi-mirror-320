import asyncio
import copy
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from ark.component.llm.base import (
    BaseChatLanguageModel,
    BaseTokenizeLanguageModel,
)
from ark.component.prompts.rag_prompt import (
    AbstractAugmentPromptTemplate,
    AugmentPromptTemplate,
    abstract_augment_prompt_template,
    faq_augment_prompt_template,
    hypo_queries_augment_prompt_template,
    summary_augment_prompt_template,
)
from ark.core._api.deprecation import deprecated
from ark.core.idl.maas_protocol import MaasChatMessage
from ark.core.rag import KnowledgeChunk, KnowledgeSchema
from ark.core.task import task
from ark.core.utils.prompt import format_maas_prompts

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s"
)
LOGGER = logging.getLogger(__name__)


@task()
async def llm_chat(
    endpoint_id: str,
    parameters: Dict[str, Any],
    messages: List[MaasChatMessage],
    retry: int = 1,
) -> str:
    for r in range(retry):
        try:
            resp = await BaseChatLanguageModel(
                endpoint_id=endpoint_id, parameters=parameters, messages=messages
            ).arun()
            if resp.error is not None:
                if resp.error.code_n in [1709820, 1709821]:
                    # RPM 超限错误码 1709820, TPM 超限错误码 1709821
                    await asyncio.sleep(5)
            assert isinstance(resp.choices[0].message.content, str)
            assert len(resp.choices[0].message.content) > 0
            return resp.choices[0].message.content
        except Exception as e:
            LOGGER.error("maas chat error, retry: %s, err: %s", r, e)
            await asyncio.sleep(1)
            continue
    raise Exception(f"maas chat error after {retry} trials")


@task()
async def llm_tokenize(
    endpoint_id: str,
    text: str,
    retry: int = 1,
) -> List[str]:
    """
    deprecated.
    """
    for r in range(retry):
        try:
            # FIXME：tokenize 接口的 "text" 限长不能超过 32768，MaaS fix 后就不用分段
            # text_tokens = await BaseTokenizeLanguageModel(
            #     endpoint_id=endpoint_id,
            #     text=text,
            # ).arun()
            tasks = [
                BaseTokenizeLanguageModel(
                    endpoint_id=endpoint_id,
                    text=text[i : i + 32768],
                ).arun()
                for i in range(0, len(text), 32768)
            ]
            resps = await asyncio.gather(*tasks)
            text_tokens: List[str] = []
            for resp in resps:
                assert resp.tokens is not None, "tokenize failed"
                text_tokens.extend(resp.tokens)
            return text_tokens
        except Exception as e:
            LOGGER.error("maas chat error, retry: %s, err: %s", r, e)
            await asyncio.sleep(1)
            continue
    raise Exception(f"maas tokenize error after {retry} trials")


@task()
async def llm_tokenize_v2(
    endpoint_id: str,
    text: str,
    retry: int = 1,
) -> List[str]:
    """
    use offset_mapping to generate text tokens
    """
    for r in range(retry):
        try:
            # tokenize 接口的 "text" 限长不能超过 131072
            split_size = 131072
            tasks = [
                BaseTokenizeLanguageModel(
                    endpoint_id=endpoint_id,
                    text=text[i : i + split_size],
                ).arun()
                for i in range(0, len(text), split_size)
            ]
            resps = await asyncio.gather(*tasks)
            text_tokens: List[str] = []
            last_left, last_right = -1, -1
            for i, resp in enumerate(resps):
                assert resp.offset_mapping is not None, "tokenize failed"
                for offset in resp.offset_mapping:
                    left = i * split_size + offset[0]
                    right = left + offset[1] - offset[0]
                    if left != last_left and right != last_right:
                        text_tokens.append(text[last_left:last_right])
                        last_left, last_right = left, right
                    else:
                        text_tokens.append("")
                        # multi tokens represent one utf-8 char
                        # use "" to fill
            text_tokens.append(text[last_left:last_right])
            text_tokens.pop(0)  # pop first "" from text[-1:-1]
            return text_tokens
        except Exception as e:
            LOGGER.error("maas chat error, retry: %s, err: %s", r, e)
            await asyncio.sleep(1)
            continue
    raise Exception(f"maas tokenize error after {retry} trials")


@task()
async def generate_abstract(
    config: KnowledgeSchema,
    full_text_chunk: KnowledgeChunk,
    endpoint_id: str,
    parameters: Dict[str, Any],
    field_name: str = "text",
    template: Optional[AbstractAugmentPromptTemplate] = None,
    overlap_tokens: int = 200,
) -> KnowledgeChunk:
    LOGGER.info("generate_abstract started")
    start_time = time.time()
    if not template:
        template = abstract_augment_prompt_template
    # Template Tokens
    tpl_tokens = await llm_tokenize_v2(
        endpoint_id=endpoint_id, text=template.template_str, retry=2
    )
    # full_text tokens
    full_text = full_text_chunk.scalars.get(field_name, None)
    assert full_text is not None, f"{field_name} not found in full_text_chunk.scalar"
    full_text_tokens = await llm_tokenize_v2(
        endpoint_id=endpoint_id, text=full_text, retry=2
    )

    # calculate split_size for full_text
    split_limit = parameters["max_prompt_tokens"] - len(tpl_tokens) - 2 * overlap_tokens
    split_num = len(full_text_tokens) // split_limit + 1
    split_size = min(
        len(full_text_tokens) // split_num, split_limit - parameters["max_new_tokens"]
    )

    LOGGER.info(
        "full_text_tokens %d, split_num: %d, augment may be slow",
        len(full_text_tokens),
        split_num,
    )

    # llm abstract
    abstract = "无"
    for i in range(0, len(full_text_tokens), split_size):
        cur_text = "".join(
            full_text_tokens[
                max(0, i - overlap_tokens) : i + split_size + overlap_tokens
            ]
        )
        messages = format_maas_prompts(
            template=template,
            chat_messages=[],
            last_abstract=abstract,
            reference=cur_text,
        )
        abstract_content = await llm_chat(
            endpoint_id=endpoint_id, parameters=parameters, messages=messages, retry=2
        )
        if len(abstract_content) == 0:
            continue
        abstract = abstract_content

    # build abstract chunk
    abstract_scalars = copy.deepcopy(full_text_chunk.scalars)
    chunk_type = "abstract"
    doc_id = full_text_chunk.scalars["doc_id"]
    chunk_id = full_text_chunk.scalars["chunk_id"]
    abstract_scalars.update(
        {
            "text": abstract,
            "chunk_type": chunk_type,
            "chunk_len": len(abstract),
        }
    )
    encode_abstract = abstract[: config.vector_text_len_limit]
    abstract_chunk = KnowledgeChunk(
        primary_key=(
            full_text_chunk.primary_key[0],
            "#".join([doc_id, chunk_type, str(chunk_id)]),
        ),
        vector=(full_text_chunk.vector[0], encode_abstract),
        scalars=abstract_scalars,
        knowledge_schema=full_text_chunk.knowledge_schema,
    )
    elapsed = time.time() - start_time
    LOGGER.info("generate_abstract finished, elapsed: %.2f seconds", elapsed)
    return abstract_chunk


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.rag_rewrite.generate_augment",
)
@task()
async def generate_agument(
    config: KnowledgeSchema,
    chunks: List[KnowledgeChunk],
    endpoint_id: str,
    parameters: Dict[str, Any],
    field_name: str = "text",
    field_prefix: str = "",
    replace_field_with_augment: bool = False,
    template: Optional[AugmentPromptTemplate] = None,
    augment_type: str = "augment",
    augment_parser: Callable[[str], List[str]] = lambda s: [s],
    augment_num_limit: int = 1,
    parallel: int = 5,
) -> List[KnowledgeChunk]:
    LOGGER.info("%s started", augment_type)
    # run augment
    augment_results = []
    for i in range(0, len(chunks), parallel):
        tasks = []
        for chunk in chunks[i : i + parallel]:
            cur_text = chunk.scalars.get(field_name, None)
            assert cur_text, f"{field_name} not found in chunk.scalar"
            messages = format_maas_prompts(
                template=template,
                chat_messages=[],
                reference=f"{field_prefix}{cur_text}",
            )
            tasks.append(
                llm_chat(
                    endpoint_id=endpoint_id,
                    parameters=parameters,
                    messages=messages,
                    retry=2,
                )
            )
        augment_results.extend(await asyncio.gather(*tasks))
        LOGGER.info(
            "%d chunks augmented, total %d chunks", len(augment_results), len(chunks)
        )
    # build augment chunks
    augment_chunks = []
    for chunk, augment_result in zip(chunks, augment_results):
        augments = augment_parser(augment_result)
        for augment in augments[:augment_num_limit]:
            augment_scalars = copy.deepcopy(chunk.scalars)
            doc_id = chunk.scalars["doc_id"]
            chunk_id = chunk.scalars["chunk_id"]
            augment_scalars["chunk_type"] = augment_type
            if replace_field_with_augment:
                augment_scalars.update({field_name: augment, "chunk_len": len(augment)})
            encode_augment = augment[: config.vector_text_len_limit]
            augment_chunks.append(
                KnowledgeChunk(
                    primary_key=(
                        chunk.primary_key[0],
                        "#".join([doc_id, augment_type, str(chunk_id)]),
                    ),
                    vector=(chunk.vector[0], encode_augment),
                    scalars=augment_scalars,
                    knowledge_schema=chunk.knowledge_schema,
                )
            )

    LOGGER.info("%s finished", augment_type)
    return augment_chunks


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.rag_rewrite.generate_summary_augment",
)
@task()
async def generate_summary_agument(
    config: KnowledgeSchema,
    chunks: List[KnowledgeChunk],
    endpoint_id: str,
    field_name: str = "text",
    field_prefix: str = "",
    parameters: Optional[Dict[str, Any]] = None,
    augment_num_limit: int = 1,
    parallel: int = 5,
) -> List[KnowledgeChunk]:
    return await generate_agument(
        config=config,
        chunks=chunks,
        endpoint_id=endpoint_id,
        field_name=field_name,
        field_prefix=field_prefix,
        replace_field_with_augment=True,
        template=summary_augment_prompt_template,
        parameters=parameters,
        augment_type="summary_augment",
        augment_parser=lambda s: [s] if len(s) > 0 and "无法提取" not in s else [],
        augment_num_limit=augment_num_limit,
        parallel=parallel,
    )


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.rag_rewrite.generate_hypo_queries_augment",
)
@task()
async def generate_hypo_queries_agument(
    config: KnowledgeSchema,
    chunks: List[KnowledgeChunk],
    endpoint_id: str,
    field_name: str = "text",
    field_prefix: str = "",
    parameters: Optional[Dict[str, Any]] = None,
    augment_num_limit: int = 1,
    parallel: int = 5,
) -> List[KnowledgeChunk]:
    return await generate_agument(
        config=config,
        chunks=chunks,
        endpoint_id=endpoint_id,
        field_name=field_name,
        field_prefix=field_prefix,
        replace_field_with_augment=False,
        template=hypo_queries_augment_prompt_template,
        parameters=parameters,
        augment_type="hypo_queries_augment",
        augment_parser=lambda s: [s] if len(s) > 0 and "无法提取" not in s else [],
        augment_num_limit=augment_num_limit,
        parallel=parallel,
    )


@deprecated(
    since="0.1.11",
    removal="0.2.0",
    alternative_import="ark.component.v3.llm.rag_rewrite.generate_faq_augment",
)
@task()
async def generate_faq_agument(
    config: KnowledgeSchema,
    chunks: List[KnowledgeChunk],
    endpoint_id: str,
    field_name: str = "text",
    field_prefix: str = "",
    parameters: Optional[Dict[str, Any]] = None,
    augment_num_limit: int = 3,
    parallel: int = 5,
) -> List[KnowledgeChunk]:
    def parse_faq_content(content: str) -> List[str]:
        faqs = []
        for qa_pair in content.split("\n\n"):
            lines = qa_pair.split("\n")
            if len(lines) == 2:
                faqs.append(f"问题：{lines[0]}\n回答：{lines[1]}")
        return faqs

    return await generate_agument(
        config=config,
        chunks=chunks,
        endpoint_id=endpoint_id,
        field_name=field_name,
        field_prefix=field_prefix,
        replace_field_with_augment=True,
        template=faq_augment_prompt_template,
        parameters=parameters,
        augment_type="faq_augment",
        augment_parser=parse_faq_content,
        augment_num_limit=augment_num_limit,
        parallel=parallel,
    )
