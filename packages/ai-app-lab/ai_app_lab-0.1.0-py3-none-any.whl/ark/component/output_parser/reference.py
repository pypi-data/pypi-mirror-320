from enum import Enum
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel
from volcenginesdkarkruntime.types.create_tokenization_response import Tokenization

from ark.core.idl.maas_protocol import Reference
from ark.core.task.task import task
from ark.core.utils.types import snake_merge


class ReferenceType(str, Enum):
    SEARCH = "search"
    RAG = "rag"


ReferenceType2TagMap = {ReferenceType.SEARCH: "联网", ReferenceType.RAG: "知识库"}


class ReferenceOrganizationInput(BaseModel):
    reference_type: ReferenceType
    references: List[Reference]
    reference_texts: List[str]
    offset_mappings: List[List[List[int]]]
    total_tokens: List[int]


class ReferenceText(BaseModel):
    """
    ReferenceText is used for reference text parsing
    """

    text: str
    """
    text stands for reference basic content
    """
    tokenization: Tokenization
    """
    tokenization is used for content length limitation
    """
    reference_type: ReferenceType
    """
    reference_type stands for tagging
    """
    reference: Reference
    """
    reference stands for metadata
    """


@task()
def parse_multiple_reference_texts(
    reference_text_list: List[List[ReferenceText]],
    max_reference_tokens: int = 6000,
    min_reference_tokens: int = 0,
) -> str:
    filtered_references: Dict[ReferenceType, List[str]] = {}

    snake_ordered_list: List[ReferenceText] = snake_merge(reference_text_list)
    for item in snake_ordered_list:  # type: ReferenceText
        prefix_length, reference_tag = (
            0,
            ReferenceType2TagMap.get(item.reference_type, ""),
        )

        item_index = len(filtered_references.get(item.reference_type, []))
        # prefix tag for calculating tokens number, not in attributes
        if item_index == 0:
            prefix_length = len(f"\n## {reference_tag}资料\n")

        # prompt begin
        attrs = f"### 资料{item_index + 1}\n"

        # travel attributes fields with not-none value
        ordered_fields_set = sorted(item.reference.model_fields_set)
        for key in ordered_fields_set:
            field_info, value = (
                item.reference.model_fields[key],
                item.reference.__dict__.get(key),
            )
            if not field_info.description or not value:
                continue
            attrs += f"- {field_info.description}：{value}\n"

        attrs += f"- {reference_tag}资料正文：\n"

        # pre-check length
        max_reference_tokens -= prefix_length + len(attrs)
        if max_reference_tokens < min_reference_tokens:
            break

        # get text content by offset_mapping & max tokens limitation
        text = _get_reference_text(
            item.text,
            item.tokenization.offset_mapping,
            item.tokenization.total_tokens,
            max_reference_tokens,
        )
        # append item & reduce the tokens number
        filtered_references.setdefault(item.reference_type, []).append(attrs + text)
        max_reference_tokens -= item.tokenization.total_tokens

    # final encoding
    reference_text = ""
    for reference_type, text_list in filtered_references.items():
        reference_tag = ReferenceType2TagMap.get(reference_type, "")
        reference_text += f"\n## {reference_tag}资料\n"

        reference_text += "\n".join(text_list)

    return reference_text


def _get_reference_text(
    text: str,
    offset_mapping: List[List[int]],
    total_tokens: int,
    max_reference_tokens: int,
) -> str:
    reference_text_tokens = (
        offset_mapping
        if max_reference_tokens > total_tokens
        else offset_mapping[:max_reference_tokens]
    )
    index_begin, index_end = 0, -1
    if reference_text_tokens and len(reference_text_tokens) > 0:
        if len(reference_text_tokens[0]) > 0:
            index_begin = reference_text_tokens[0][0]
        if len(reference_text_tokens[-1]) > 1:
            index_end = reference_text_tokens[-1][1]

    return text[index_begin:index_end]


@task()
async def parse_reference(
    tokens: List[List[str]],
    total_tokens: List[int],
    references: List[Reference],
    max_reference_token: int = 6000,
    min_reference_token: int = 200,
) -> str:
    # lower bound for reference trim
    prefix_suffix_tokens = 12
    # tokens=['\n', '<', '资料', '{i+1}', '开始', '>\n']
    reference_text = ""
    for i, (token, total_token) in enumerate(zip(tokens, total_tokens)):
        max_reference_token -= prefix_suffix_tokens
        if max_reference_token <= min_reference_token:
            break
        reference_text += f"\n<资料{i + 1}开始>\n"
        attrs = ""
        if i < len(references):
            if references[i].title:
                attrs += f"标题：{references[i].title}\n"
            if references[i].site_name:
                attrs += f"来源：{references[i].site_name}\n"
            if references[i].freshness_info:
                attrs += f"时效性：{references[i].freshness_info}\n"
            if references[i].publish_time:
                attrs += f"发布时间：{references[i].publish_time}\n"
        attrs += "资料正文：\n"
        reference_text += attrs
        max_reference_token -= len(attrs)  # attrs 直接用 len 当做 token len
        reference_text += (
            "".join(token)
            if max_reference_token > total_token
            else "".join(token[:max_reference_token])
        )
        reference_text += f"\n<资料{i + 1}结束>\n"
        max_reference_token -= total_token
    return reference_text


@task()
async def parse_reference_with_offset_mapping(
    origin_texts: List[str],
    offset_mappings: List[List[List[int]]],
    total_tokens: List[int],
    references: List[Reference],
    max_reference_token: int = 6000,
    min_reference_token: int = 200,
    reference_type: Optional[ReferenceType] = None,
) -> str:
    if (
        len(origin_texts) == 0
        or len(offset_mappings) == 0
        or len(total_tokens) == 0
        or len(references) == 0
    ):
        return ""

    # lower bound for reference trim
    prefix_suffix_tokens = 12
    # tokens=['\n', '<', '资料', '{i+1}', '开始', '>\n']
    reference_text, reference_tag = "", ""
    if reference_type is not None:
        reference_tag = ReferenceType2TagMap.get(reference_type, "")
        reference_text += f"\n## {reference_tag}资料"
    for i, (offset_mapping, total_token) in enumerate(
        zip(offset_mappings, total_tokens)
    ):
        max_reference_token -= prefix_suffix_tokens
        if max_reference_token <= min_reference_token:
            break

        if reference_type is None:
            reference_text += f"\n<资料{i + 1}开始>\n"
        else:
            reference_text += f"\n### 资料{i + 1}\n"

        attrs = ""
        if i < len(references):
            if references[i].title:
                attrs += f"- 标题：{references[i].title}\n"
            if references[i].site_name:
                attrs += f"- 来源：{references[i].site_name}\n"
            if references[i].freshness_info:
                attrs += f"- 时效性：{references[i].freshness_info}\n"
            if references[i].publish_time:
                attrs += f"- 发布时间：{references[i].publish_time}\n"
            if references[i].doc_id:
                attrs += f"- 文档ID：{references[i].doc_id}\n"
            if references[i].doc_name:
                attrs += f"- 文档名：{references[i].doc_name}\n"
            if references[i].doc_type:
                attrs += f"- 文档类型：{references[i].doc_type}\n"
            if references[i].doc_title:
                attrs += f"- 文档标题：{references[i].doc_title}\n"
            if references[i].chunk_title:
                attrs += f"- 分块标题：{references[i].chunk_title}\n"
            if references[i].chunk_id:
                attrs += f"- 分块编号：{references[i].chunk_id}\n"

        attrs += f"- {reference_tag}资料正文：\n"
        reference_text += attrs
        max_reference_token -= len(attrs)  # attrs 直接用 len 当做 token len

        reference_text += _get_reference_text(
            origin_texts[i], offset_mapping, total_token, max_reference_token
        )

        # compatible with older version
        if not reference_type:
            reference_text += f"\n<资料{i + 1}结束>\n"
        max_reference_token -= total_token
    return reference_text


@task()
def merge_reference_pair(
    reference_pair: Tuple[List[Reference], List[Reference]],
) -> List[Reference]:
    reference_first, reference_second = reference_pair
    merged_reference_list: List[Reference] = []
    for i in range(len(reference_first)):
        merged_dict = {
            **reference_first[i].model_dump(exclude_none=True, exclude_unset=True),
            **reference_second[i].model_dump(exclude_none=True, exclude_unset=True),
        }
        merged_reference = Reference(**merged_dict)
        merged_reference_list.append(merged_reference)
    return merged_reference_list
