from typing import Any, List, Union

from jinja2 import Template
from langchain.prompts.chat import BaseChatPromptTemplate
from langchain.schema.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    get_buffer_string,
)
from pydantic.v1 import validator


class AbstractAugmentPromptTemplate(BaseChatPromptTemplate):
    """Abstract augment prompt template."""

    input_variables: List[str] = ["messages"]
    """List of input variables in template messages. Used for validation."""

    template: Template

    @validator("template", pre=True)
    @classmethod
    def validate_template(cls, v: Union[str, Template]) -> Template:
        if isinstance(v, str):
            return Template(source=v)
        return v

    @property
    def template_str(self) -> str:
        """Return the template string."""
        return self.template.render()

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        """Format original messages into a list of messages.
        Args:
            messages: list of original messages.
        Returns:
            Formatted message
        """
        if "reference" not in kwargs:
            raise ValueError("Must provide reference: str")
        reference = kwargs.pop("reference")
        if "last_abstract" not in kwargs:
            raise ValueError("Must provide last_abstract: str")
        last_abstract = kwargs.pop("last_abstract")

        abstract_user_prompt = self.template.render(
            last_abstract=last_abstract, reference=reference, **kwargs
        )
        return [HumanMessage(content=abstract_user_prompt, additional_kwargs=kwargs)]


class AugmentPromptTemplate(BaseChatPromptTemplate):
    """summary augment for chunk prompt template."""

    input_variables: List[str] = ["messages"]
    """List of input variables in template messages. Used for validation."""

    template: Template

    @validator("template", pre=True)
    @classmethod
    def validate_template(cls, v: Union[str, Template]) -> Template:
        if isinstance(v, str):
            return Template(source=v)
        return v

    @property
    def template_str(self) -> str:
        """Return the template string."""
        return self.template.render()

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        """Format original messages into a list of messages.
        Args:
            messages: list of original messages.
        Returns:
            Formatted message
        """
        if "reference" not in kwargs:
            raise ValueError("Must provide reference: str")
        reference = kwargs.pop("reference")

        prompt = self.template.render(reference=reference, **kwargs)
        return [HumanMessage(content=prompt, additional_kwargs=kwargs)]


class RagInnerPromptTemplate(BaseChatPromptTemplate):
    """prompt template for intent and query rewrite."""

    input_variables: List[str] = ["messages"]
    """List of input variables in template messages. Used for validation."""

    template: Template
    keep_human_history: bool = True
    keep_ai_history: bool = True
    max_history_len: int = 0

    @validator("template", pre=True)
    def validate_template(cls, v: Union[str, Template]) -> Template:
        if isinstance(v, str):
            return Template(source=v)
        return v

    @property
    def template_str(self) -> str:
        """Return the template string."""
        return self.template.render()

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        """Format original messages into a list of messages.

        Args:
            messages: list of original messages.

        Returns:
            Formatted message
        """
        if "messages" not in kwargs:
            raise ValueError("Must provide messages: List[BaseMessage]")
        messages = kwargs.pop("messages")
        histories: List[Union[AIMessage, HumanMessage]] = []
        if len(messages) == 0:
            raise ValueError("No user question found in the request")
        elif len(messages) > 1:
            current = messages[-1]
            for msg in messages[:-1]:
                if isinstance(msg, HumanMessage) and self.keep_human_history:
                    histories.append(msg)
                elif isinstance(msg, AIMessage) and self.keep_ai_history:
                    histories.append(msg)
        else:
            histories, current = [], messages[0]

        if self.max_history_len > 0:
            history_len = sum([len(msg.content) for msg in histories])
            while history_len > self.max_history_len:
                history_len -= len(histories.pop(0).content)

        if len(histories) > 0:
            chat_history = get_buffer_string(
                histories, human_prefix="User", ai_prefix="Assistant"
            )
        else:
            chat_history = "无"
        prompt = self.template.render(
            chat_history=chat_history, question=current.content, **kwargs
        )

        return [HumanMessage(content=prompt, additional_kwargs=kwargs)]


class IntentionPromptTemplate(RagInnerPromptTemplate):
    """Retriever intention template."""

    keep_human_history: bool = True
    keep_ai_history: bool = False
    max_history_len: int = 1000


class QueryRewritePromptTemplate(RagInnerPromptTemplate):
    """Retriever condense question prompt template."""

    keep_human_history: bool = True
    keep_ai_history: bool = True
    max_history_len: int = 2000


ABSTRACT_AUGMENT_TEMPLATE = Template(
    """# 角色
你是一个擅长总结摘要的专家，根据用户的参考资料和要求，生成总结摘要。

# 参考资料
## 新增资料
<资料开始>
{{reference}}
<资料结束>

## 前文总结
{{last_abstract}}

# 要求
1. 结合参考资料中的「前文总结」和「新增资料」，\
「前文总结」的信息必须完整保留，将「前文总结」和「新增资料」合并为完整的总结摘要；
2. 如果「前文总结」和「新增资料」识别到章节、分段等信息，则分章节进行汇总摘要；
3. 分段进行总结汇总，不能过于简略，保留参考资料的关键信息，包括但不限于：\
人名、地名、有名称的实体、时间、发生的事件、影响面、讨论的对象；
4. 可以直接引用重要的片段，重要的任务、对象在首次出现时必须使用完整的名称，\
注意引用次数不超过 5 次；
5. 直接输出总结摘要标题和正文，第一行是摘要的标题，第二行开始是摘要内容，\
无需添加任何开始和结束的标志，不要使用 markdown 格式，不要添加“正文摘要：”等前缀和说明

## 样例输出格式
《简述牛顿和天体力学》的摘要
艾萨克·牛顿（Isaac Newton）通过观察苹果落地的现象，深入思考并进行了一系列的实验和研究，\
最终发现了重力的存在和作用原理。
牛顿在他的著作《天体力学》，在这一领域他提出了行星运动的三定律，并利用万有引力定律解释了行星轨道的形状和运动规律：
第一定律（椭圆轨道定律）：行星绕太阳运动的轨道是一个椭圆，太阳位于椭圆的一个焦点上。
第二定律（面积速度定律）：行星在其轨道上的运动速度随其位置的变化而变化。当行星离太阳较近的时，\
它沿着轨道移动快；而当行星离太阳远时，它移动更慢，行星在相同时间内扫过的面积相等。
第三定律（调和定律）：行星轨道的周期与其轨道半长轴的关系成正比。行星离太阳越远，绕太阳运动所需的时间就越长。

# 任务
请根据上述要求和参考资料进行总结摘要
"""
)
abstract_augment_prompt_template = AbstractAugmentPromptTemplate(
    template=ABSTRACT_AUGMENT_TEMPLATE
)

SUMMARY_AUGMENT_TEMPLATE = Template(
    """# 角色
你是一位善于对「用户输入」进行重写的文本处理专家，在保证信息完整性的前提下，对文本进行总结重写。

# 约束
1. **列举主体时，必须保留「用户输入」中出现的全部对象，不得省略，且保留完整名称**；
2. 去除冗余信息，将类比、比喻、举例说明都精简为直接的形容词；
3. 使用平铺直叙的句式，将倒装句、反问句都转述为简短的直叙；
4. 直接输出符合要求的文本，不解释自己或者提供任何与摘要无关的信息，\
不要添加“以下是生成的摘要”等字句。
5. 如果「用户输入」无法提取有效的信息，例如「用户输入」是表格的片段、\
完全缺失语义信息的乱码，只输出"无法提取"；

# 任务
对用户输入执行信息提取，输出两行内容，第一行直接列举文本中出现的所有实体对象，\
第二行为总结重写文本，**确保信息的完整性**

## 样例输入输出
用户输入：
阿吉教你选择健康环保的水瓶，目前来看最安全的用玻璃，因为玻璃具有良好的热稳定性，\
最方便的用塑料，不易碎且轻便，但塑料有不同级别的安全性，最好使用安全性较高就选不含双酚A的PPSU塑料。

样例输出：
对象：阿吉、玻璃、塑料、双酚A、PPSU塑料
总结：选择水瓶时，要考虑安全性和便利性，玻璃和塑料各有优势。用玻璃最安全，\
但不如塑料轻便，高价的不含双酚A的PPSU塑料兼顾安全和便利。

# 用户输入
{{reference}}
"""
)
summary_augment_prompt_template = AugmentPromptTemplate(
    template=SUMMARY_AUGMENT_TEMPLATE
)

HYPO_QUERIES_AUGMENT_TEMPLATE = Template(
    """# 角色
你是一个文本处理专家，擅长对文本进行抽取和归纳出问题，最后输出成更简洁和清晰的问题，提出可以使用「用户输入」来回答的问题。

# 约束
- 先推理并替换掉「用户输入」中的指示代词，生成出来的问题要有清晰的主语，\
禁止使用指示代词；
- 补全或改写「用户输入」中的关键词，并保留到问题中，\
尽可能地包含「用户输入」中的关键词和实体词；
- 从不同角度提出「用户输入」主题有代表性的问题，\
问题可以从时间、地点、人物、事件、影响等多个角度抽取；
- 每个问题一行，不要添加序号和问题以外的任何内容，\
不要解释自己，不要重复；
- 如果「用户输入」无法提取有效的信息，\
例如「用户输入」是表格的片段、完全缺失语义信息的乱码，只输出"无法提取"；

# 任务
对用户输入执行信息提取，将「用户输入」分段按顺序抽取1~10个问题

## 样例输入输出
用户输入：
苹果会落在地上是因为地球对它施加了引力，也就是重力。重力是一种基本的物理现象，它导致物体受到朝向地球中心的吸引力。\
具体来说，地球的质量非常大，这使得它对周围的物体产生了引力。当苹果挂在树上时，树枝对苹果有一个支撑力，使其保持在树上。\
但是，当支撑力消失（例如树枝断裂或苹果自然脱落）时，苹果就会受到重力的作用而向下掉落。\
牛顿通过观察苹果落地的现象，深入思考并进行了一系列的实验和研究，最终发现了重力的存在和作用原理。

样例输出：
为什么苹果会落在地上，是什么导致了这种下落的物理现象？
重力为什么会导致苹果从树上掉落到地面？
牛顿是怎么从苹果落地发现重力的？

# 用户输入
{{reference}}
"""
)
hypo_queries_augment_prompt_template = AugmentPromptTemplate(
    template=HYPO_QUERIES_AUGMENT_TEMPLATE
)

FAQ_AUGMENT_TEMPLATE = Template(
    """# 角色
你是一个文本处理专家，擅长对文本进行抽取和归纳出高频问题和回答，根据「用户输入」构造出问答对话。

# 约束
- 先推理并替换掉「用户输入」中的指示代词，\
生成出来的问题要有清晰的主语，禁止使用指示代词。
- 补全或改写「用户输入」中的关键词，并保留到问题中，\
尽可能地包含「用户输入」中的关键词和实体词。
- 从不同角度提出「用户输入」主题有代表性的问题，多个角度提问和回答，\
例如：「用户输入」是一条新闻，可以从时间、地点、人物、事件、影响面等角度提问；\
「用户输入」是一段说明书，可以从产品特性、功能、故障现象等角度提问。
- 每个问题一行，不要添加序号和问答对以外的任何内容，不要解释自己，不要重复。
- 如果「用户输入」无法提取有效的信息，\
例如「用户输入」是表格的片段、完全缺失语义信息的乱码，只输出一次"无法提取"。

# 任务
对用户输入执行信息提取，将「用户输入」分段按抽取成多个问答对，问题和答案各占一行，每个问答对之间空一行。
若能提取，第一个问答必须是针对「用户输入」全文的提问和回答，之后的问答对针对分段细节提问和回答。

## 样例输入输出
用户输入：
苹果会落在地上是因为地球对它施加了引力，也就是重力。\
重力是一种基本的物理现象，它导致物体受到朝向地球中心的吸引力。\
具体来说，地球的质量非常大，这使得它对周围的物体产生了引力。\
当苹果挂在树上时，树枝对苹果有一个支撑力，使其保持在树上。\
但是，当支撑力消失（例如树枝断裂或苹果自然脱落）时，\
苹果就会受到重力的作用而向下掉落。牛顿通过观察苹果落地的现象，\
深入思考并进行了一系列的实验和研究，最终发现了重力的存在和作用原理。

样例输出：
为什么苹果会落在地上，是什么导致了这种下落的物理现象？
苹果落地是因为地球的重力产生的物理现象，重力对物体产生朝向地球中心的吸引力。

重力为什么会导致苹果从树上掉落到地面？
重力本身不直接导致苹果掉落地面，当苹果挂在树上时，树枝对苹果有一个支撑力，使其保持在树上。\
但是，当支撑力消失（例如树枝断裂）时，重力大于支撑力，使得苹果向下掉落。

牛顿是怎么从苹果落地发现重力的？
牛顿通过观察察苹果落地，深入思考并进行实验和研究，最终发现了重力的存在和作用原理。

# 用户输入
{{reference}}
"""
)
faq_augment_prompt_template = AugmentPromptTemplate(template=FAQ_AUGMENT_TEMPLATE)

CONDENSE_QUESTION_PROMPT_TEMPLATE = Template(
    """# 角色
你是一个检索专家，擅长根据「聊天记录」和「新问题」，进行信息提取并将问题重写为适用于检索的新问题。

# 约束
- 先推理并替换掉「新问题」中的指示代词，生成出来的问题要有清晰的主语，禁止使用指示代词；
- 补全或改写「新问题」中的关键词，并保留到问题中，\
尽可能地包含「聊天记录」和「新问题」关联的关键词和实体词；
- 不要添加序号和问题以外的任何内容，不要解释自己，不要重复；

# 聊天记录
{{chat_history}}

# 新问题: 
{{question}}

# 任务
结合「聊天记录」和「新问题」，将新问题重新表述为单个完整独立的问题，直接输出重新表述的问题，不要添加根据聊天记录等话语。
"""
)
condense_question_prompt_template = QueryRewritePromptTemplate(
    template=CONDENSE_QUESTION_PROMPT_TEMPLATE
)

HYPO_ANSWER_PROMPT_TEMPLATE = Template(
    """# 角色
你是一个百科专家，擅长根据「聊天记录」和一个「新问题」，生成一段相关资料作为回答，可以忽略答案的事实性。

# 约束
- 先推理并替换掉「新问题」中的指示代词，生成出来的语料要有清晰的主语，禁止使用指示代词；
- 补全或改写「新问题」中的关键词，尽可能地包含「新问题」中的关键词和实体词；
- 不要添加序号和相关资料以外的任何内容，不要解释自己，不要重复；

# 聊天记录
{{chat_history}}

# 问题
{{question}}

# 任务
生成一段相关资料作为「新问题」的回答。
"""
)
hypo_answer_prompt_template = QueryRewritePromptTemplate(
    template=HYPO_ANSWER_PROMPT_TEMPLATE
)

KNOWLEDGE_INTENTION_TEMPLATE = Template(
    """请你根据历史对话记录和用户问题，判断你是否需要检索信息，回答用户问题。

请你以如下的格式回答：
回答只有一行，只能是"无需检索"或者"需要检索"，不要再进行任何补充描述。

历史问题记录:
{{chat_history}}

用户问题:
{{question}}

回答:
"""
)

ABSTRACT_INTENTION_TEMPLATE = Template(
    """请判断回答用户问题是否要用到参考资料的摘要信息?

示例:
xx论文的摘要是什么?->是
xx的主要内容是什么?->是
xx的yy章节主要内容是?->否
xx论文中在zz情况下应该怎么做?->否

请你以如下的格式回答：
回答只有一行，只能是"无需检索"或者"需要检索"，不要再进行任何补充描述。

用户问题:
{{question}}

回答:
"""
)

DEFAULT_SUMMARY_PROMPT = Template(
    """# 参考资料
{{reference}}

# 任务和限制
你需要根据参考资料来回答用户的问题，解决用户关于百科问题的疑问，你的回答需要准确和完整。

你的回答要满足以下几个限制：
1. 回答内容必须在参考资料范围内，不能做任何参考资料以外的扩展解释。
2. 如果参考资料不能帮助你回答用户问题，请回答“抱歉，这个问题我还不会”。
3. 你的回答不能暴露参考资料的存在，回答内容不能包含诸如“根据提供的参考资料”，\
“根据我的知识库”等，直接回答跟用户问题有关的内容即可。

# 任务执行
现在请你根据提供的参考资料，遵循限制来回答用户的问题，你的回答需要准确和完整。

用户问题：
{{question}}

完整、详细、有帮助的回答：
"""
)

RAG_INTENTION_TEMPLATE = Template(
    """# 任务描述
请根据「历史记录」和「用户问题」，判断应该以下哪些内容源哪些可以获得有助于回答用户问题的资料：
{{sources_desc_text}}

# 任务要求
1. 可以选择{{enum_list_text}}，或者选择「无需检索」，不要再进行任何补充描述；
2. 如果是闲聊或者是内容源无关的用户问题等情景，不需要额外信息帮助回答问题，只输出「无需检索」；

# 执行任务
历史记录：
{{chat_history}}

用户问题：
{{question}}

判断结果：
"""
)

# -*- Query Rewrite -*- #
RAG_REWRITE_PROMPT_TEMPLATE = Template(
    """# 聊天记录
{{chat_history}}
<聊天记录结束>

# 用户提问
{{question}}

# 角色
你是一个检索专家，擅长根据「聊天记录」和「用户提问」，进行信息提取并将问题重写为适用于检索的1~3个问题。

# 约束
- 先推理并替换掉「用户提问」中的指示代词，生成出来的问题要有清晰的主语，禁止使用指示代词；
- 补全或改写「用户提问」中的关键词，并保留到问题中，尽可能地包含「聊天记录」和「用户提问」关联的关键词和实体词；
- 直接输出重新表述的问题，不要添加根据聊天记录等话语，不要添加序号和问题以外的任何内容，不要解释自己，不要重复；

# 任务
结合「聊天记录」和「用户提问」，将用户提问重新表述为若干个完整且独立的问题，每行输出一个改写的问题，每个问题不超过100字；
第一个改写的问题保持和「用户提问」的拥有一致的意思，从第二个改写问题开始，提出有助于检索相关资料的问题。

改写的问题：
"""
)

# -*- Summary Generation -*- #
RAG_SUMMARY_TEMPLATE = Template(
    """# 历史对话
{{chat_history}}

# 参考资料
{{reference}}

# 当前环境信息
{{meta_info}}

# 参考资料
{{reference}}

# 任务
{{task_description}}

# 任务执行
现在请你根据提供的参考资料，遵循限制来回答用户的问题，你的回答需要准确和完整；

用户问题：
{{question}}

你的回答：
"""
)

RAG_STRICT_TASK_DESCRIPTION = """- 你需要根据「参考资料」和「当前环境信息」完整、详细、有帮助的回答「用户问题」。
- 你的回答要满足以下几个限制：
    1. 回答内容必须在参考资料范围内，不能做任何参考资料以外的扩展解释；
    2. 如果参考资料不能帮助你回答用户问题，请回答“抱歉，这个问题我还不会，尝试告诉我更多信息吧”；
    3. 你的回答不能暴露参考资料的存在，回答内容不能包含诸如“根据提供的参考资料”，“根据我的知识库”等，直接回答跟用户问题有关的内容即可；
"""

RAG_PARTIAL_TASK_DESCRIPTION = """
- 你需要根据「参考资料」和「当前环境信息」完整、详细、有帮助的回答「用户问题」；
- 回答问题时，先查阅与「用户问题」有关联的「参考资料」、「当前环境信息」，结合你自己的知识，汇总信息后，给出对「用户问题」有帮助的回答；
- 你的回答要满足以下几个限制：
    1. 使用专业的语言风格回答，你的知识和参考资料不一致时，以参考资料为准；
    2. 回答内容不能包含诸如“根据提供的参考资料”，“根据我的知识库”等，直接回答跟用户问题有关的内容即可；
"""
