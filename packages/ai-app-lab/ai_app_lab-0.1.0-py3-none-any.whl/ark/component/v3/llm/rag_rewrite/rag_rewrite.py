import asyncio
import copy
from typing import Any, Callable, Dict, List, Optional

from langchain_core.output_parsers import BaseTransformOutputParser
from pydantic.v1 import Field
from typing_extensions import Literal

from ark.component.output_parser.rag_output import RagRewriteMessageChunkOutputParser
from ark.component.prompts.rag_prompt import (
    CONDENSE_QUESTION_PROMPT_TEMPLATE,
    HYPO_ANSWER_PROMPT_TEMPLATE,
    AugmentPromptTemplate,
    QueryRewritePromptTemplate,
    faq_augment_prompt_template,
    hypo_queries_augment_prompt_template,
    summary_augment_prompt_template,
)
from ark.component.v3.llm.base import BaseChatLanguageModel, BaseChatPromptTemplate
from ark.core.idl.ark_protocol import ArkChatParameters
from ark.core.rag import KnowledgeChunk, KnowledgeSchema
from ark.core.task import task
from ark.core.utils.prompt import format_maas_prompts


def _get_query_rewrite_prompt_template() -> BaseChatPromptTemplate:
    return QueryRewritePromptTemplate(template=CONDENSE_QUESTION_PROMPT_TEMPLATE)


def _get_hypo_answer_rewrite_prompt_template() -> BaseChatPromptTemplate:
    return QueryRewritePromptTemplate(template=HYPO_ANSWER_PROMPT_TEMPLATE)


def _get_default_output_parser() -> BaseTransformOutputParser:
    return RagRewriteMessageChunkOutputParser()


class RewriteGenerator(BaseChatLanguageModel):
    name: Literal["Rewrite", "QueryRewrite", "HypoAnswer"] = "Rewrite"
    template: BaseChatPromptTemplate
    output_parser: BaseTransformOutputParser[List[str]] = Field(
        default_factory=_get_default_output_parser
    )

    def _get_prompt_template(self) -> BaseChatPromptTemplate:
        return self.template

    def _get_output_parser(self) -> BaseTransformOutputParser:
        return self.output_parser

    @task()
    async def arun(self, *args: Any, **kwargs: Any) -> List[str]:
        resp = await super().arun(*args, **kwargs)
        return await self.aparse_output(resp.choices[0].message.content)

    @task()
    def run(self, *args: Any, **kwargs: Any) -> List[str]:
        resp = super().run(*args, **kwargs)
        return self.parse_output(resp.choices[0].message.content)


class QueryRewriteGenerator(RewriteGenerator):
    name: Literal["QueryRewrite"] = "QueryRewrite"
    template: BaseChatPromptTemplate = Field(
        default_factory=_get_query_rewrite_prompt_template
    )


class HypoAnswerGenerator(RewriteGenerator):
    name: Literal["HypoAnswer"] = "HypoAnswer"
    template: BaseChatPromptTemplate = Field(
        default_factory=_get_hypo_answer_rewrite_prompt_template
    )


@task()
async def generate_augment(
    config: KnowledgeSchema,
    chunks: List[KnowledgeChunk],
    endpoint_id: str,
    parameters: Optional[ArkChatParameters] = None,
    field_name: str = "text",
    field_prefix: str = "",
    replace_field_with_augment: bool = False,
    template: Optional[AugmentPromptTemplate] = None,
    augment_type: str = "augment",
    augment_parser: Callable[[str], List[str]] = lambda s: [s],
    augment_num_limit: int = 1,
    parallel: int = 5,
) -> List[KnowledgeChunk]:
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
                BaseChatLanguageModel(
                    endpoint_id=endpoint_id, parameters=parameters, messages=messages
                ).arun()
            )
        augment_results.extend(await asyncio.gather(*tasks))

    # build augment chunks
    augment_chunks = []
    for chunk, augment_resp in zip(chunks, augment_results):
        augment_result = augment_resp.choices[0].message.content
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

    return augment_chunks


@task()
async def generate_summary_augment(
    config: KnowledgeSchema,
    chunks: List[KnowledgeChunk],
    endpoint_id: str,
    field_name: str = "text",
    field_prefix: str = "",
    parameters: Optional[Dict[str, Any]] = None,
    augment_num_limit: int = 1,
    parallel: int = 5,
) -> List[KnowledgeChunk]:
    return await generate_augment(
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


@task()
async def generate_hypo_queries_augment(
    config: KnowledgeSchema,
    chunks: List[KnowledgeChunk],
    endpoint_id: str,
    field_name: str = "text",
    field_prefix: str = "",
    parameters: Optional[Dict[str, Any]] = None,
    augment_num_limit: int = 1,
    parallel: int = 5,
) -> List[KnowledgeChunk]:
    return await generate_augment(
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


@task()
async def generate_faq_augment(
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

    return await generate_augment(
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
