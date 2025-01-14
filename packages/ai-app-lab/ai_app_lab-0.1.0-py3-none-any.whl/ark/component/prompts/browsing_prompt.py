from __future__ import annotations

import time
from datetime import datetime
from typing import Any, List, Tuple, Union

from jinja2 import Template
from langchain.prompts.chat import BaseChatPromptTemplate
from langchain.schema.messages import BaseMessage, HumanMessage


class BrowsingIntentionChatPromptTemplate(BaseChatPromptTemplate):
    """Browsing Intention prompt template."""

    input_variables: List[str] = ["messages"]
    """List of input variables in template messages. Used for validation."""

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

        questions = [msg.content for msg in messages if msg.type == "human"]
        if len(questions) == 0:
            raise ValueError("No user question found in the request")
        elif len(questions) > 1:
            histories, current = questions[:-1], questions[-1]
        else:
            histories, current = [], questions[0]

        while sum(len(msg) for msg in histories) > 1000:
            histories.pop(0)

        prompt = "\n".join(
            [
                *[f"前文问题:{q}" for q in histories],
                "请判断你是否需要借助搜索引擎来回答下面的问题，请回答需要或者不需要。",
                f"问题：{current}",
            ]
        )

        return [HumanMessage(content=prompt, additional_kwargs=kwargs)]


class BrowsingGenerationChatPromptTemplate(BaseChatPromptTemplate):
    """Browsing Generation prompt template."""

    input_variables: List[str] = ["messages"]
    """List of input variables in template messages. Used for validation."""

    def _gen_meta_info(
            self,
            time_info: Union[datetime, None] = None,
            location_info: Union[Tuple[str, str], None] = None,
    ) -> str:
        city, district = location_info if location_info else ("", "")

        weekdays = [
            "星期一",
            "星期二",
            "星期三",
            "星期四",
            "星期五",
            "星期六",
            "星期日",
        ]  # `tm_wday` 0~6, 6 means Sunday
        if time_info is None:
            t = time.localtime(time.time())
            _time_info = time.strftime("%Y年%m月%d日%H时", t)
            _time_info += weekdays[t.tm_wday]
        else:
            _time_info = time_info.strftime("%Y年%m月%d日%H时")
            _time_info += weekdays[time_info.weekday()]

        meta_info = f"当前时间：{_time_info}"
        if city or district:
            meta_info += f"，当前位置：{city or ''}{district or ''}"
        return meta_info

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        """Format original messages into a list of messages.

        Args:
            messages: list of original messages.
            time_info: datetime, if not provided use current time.
            location_info: tuple[str, str], city and district

        Returns:
            Formatted message
        """
        if "messages" not in kwargs:
            raise ValueError("Must provide messages: List[BaseMessage]")

        messages = kwargs.pop("messages")
        format_messages: List[BaseMessage] = [
            msg.copy(deep=True) for msg in messages if msg.type in {"human", "ai"}
        ]

        if len(format_messages) == 0:
            return format_messages

        # 最多参考几轮历史对话
        max_history_len = kwargs.pop("max_history_len", None)
        if max_history_len is not None:
            format_messages = format_messages[-(max_history_len * 2 + 1):]

        meta_info = self._gen_meta_info(
            time_info=kwargs.pop("time_info", None),
            location_info=kwargs.pop("location_info", None),
        )

        format_messages[-1].content = "\n".join(
            [
                meta_info,
                "如果你希望借助搜索引擎回答下面的问题，你会如何搜索。如果需要搜索多次，请用[next]分割。",
                f"问题：{format_messages[-1].content}",
            ]
        )
        return format_messages


MULTI_INTENTION_TEMPLATE = Template(
    """# 任务描述
请根据「历史记录」和「用户问题」，判断应该以下哪些内容源哪些可以获得有助于回答「用户问题」的资料：
{{sources_desc_text}}

# 任务要求
- 可以选择{{enum_list_text}}，或者选择「无需检索」，不要再进行任何补充描述；
{{task_description}}

# 执行任务
遵循任务要求，判断哪些内容源哪些可以获得有助于回答「用户问题」的资料，只需输出内容源，不用描述原因。

历史记录：
<历史记录开始>
{{chat_history}}
<历史记录结束>

用户问题：
{{question}}

判断结果：
"""
)

DEFAULT_TASK_DESCRIPTION = """- 对于需要补充外部信息才能回答的问题，至少选择一个内容源；
- 天气类、新闻类、实时信息类等时效性问题，或提到[最近]，[今天]，[本周]，[这个月]，[几号]等时间信息，至少选择一个内容源。
- 如果用户问题为闲聊，或问题与内容源无关，或问题不需要额外信息帮助回答，只输出「无需检索」；
-「历史记录」和「用户问题」无关联时，只通过「用户问题」判断，忽略「历史记录」；
"""

QUERY_REWRITE_PROMPT_TEMPLATE = Template(
    """# 角色
你是一个搜索专家，擅长将「用户提问」优化为1~2个适用于搜索引擎的「搜索词」，之后用于搜索有用的资料。

# 任务要求
- 如果用户问题和「历史记录」没有直接上下文关系，改写时忽略历史记录；
- 如果用户提问信息不充分，且「历史记录」有相关上下文，结合「历史记录」进行改写；
- 直接输出「搜索词」，多个搜索词之间用"\n"隔开，输出必须纯文本，不能输出其他任何内容；
- 「搜索词」不超过2个，尽量只输出1个搜索词；
- 如果问题有时效性地域性，结合「当前环境信息」进行改写，将“今天”、“昨天”、“本地” 等相对时间和地理位置使用准确的日期和地理位置添加到搜索词中；
- 如果用户询问的问题有关穿衣建议、户外活动建议或者防护防晒建议，请将「未来天气」也添加到搜索词中；
- 如果用户询问未来天气相关信息，请确保将关键词“未来天气”和用户感兴趣的地理位置添加到搜索词中，地理位置需要是正式的行政区划名，例如“北京未来天气”、“深圳南山区未来天气”等；
- 如果用户想对节日进行日期计算，你需要在「搜索词」中加入合适的年份：
    + 如用户询问某节日已经过去多少天，「搜索词」应有2行，分别加入去年({{last_year}})和今年({{current_year}})的年份
    + 如果用户询问某节日详情（或某节日还剩多少天），「搜索词」应有2行，分别加入今年({{current_year}})和明年({{next_year}})的年份

# 执行任务
遵循任务要求，将「用户提问」优化为1~2个完整独立的利于搜索引擎使用的「搜索词」，「搜索词」不超过100字。

当前环境信息：
{{meta_info}}

历史记录：
<历史记录开始>
{{chat_history}}
<历史记录结束>

用户问题：
{{question}}

优化后的「搜索词」：
"""
)

CUSTOM_SUMMARY_PROMPT = Template(
    """# 历史对话
{{chat_history}}

# 参考资料
{{reference}}

# 当前环境信息
{{meta_info}}

# 任务
{{task_description}}

# 任务执行
遵循任务要求来回答「用户问题」，给出有帮助的回答。

用户问题：
{{question}}

# 你的回答：
"""
)

BROWSING_PARTIAL_TASK_DESCRIPTION = """你要结合最新从各种来源搜索得到的「参考资料」和「当前环境信息」回答「用户问题」。
回答问题时，先查阅与「用户问题」有关联的「参考资料」、「当前环境信息」，结合你自己的知识，汇总信息后，给出对「用户问题」有帮助的回答。

回答要满足以下要求：
1. 使用专业的语言风格回答，使用参考资料时重新组织语言，不得直接复述参考资料；
2. 时效性的问题优先参考以下来源：墨迹天气、搜索引擎；
3. 严肃的问题优先参考以下来源：抖音百科、知识库；
4. 当回答时间、日期、节日的相关问题时，你可以将「当前时间」作为提问时的具体时间，如果「参考资料」没有提供信息，请根据「当前时间」给出一个计算结果
5. 「参考资料」中的国际时间可能有误，要综合「当前时间」考虑并计算
6. 不要在回答中描述参考资料的来源或序号，不能输出“根据参考资料X”、“资料X中提到”、“未获取资料”等说法，不要解释自己；
7. 请牢记下周、本周、上周开始日期都是星期一，例如 “2024年6月13日 星期四”的下周指的是“2024年6月17日 星期一 至 2024年6月23日 星期日”，本周指的是“2024年6月10日 星期一 至 2024年6月16日 星期日”，上周指的是“2024年6月3日 星期一 至 2024年6月9日星期日” ；
"""

BROWSING_STRICT_TASK_DESCRIPTION = """你要结合最新从各种来源搜索得到的「参考资料」和「当前环境信息」回答「用户问题」。
回答问题时，先查阅与「用户问题」有关联的「参考资料」、「当前环境信息」，汇总信息后，给出对「用户问题」有帮助的回答。

回答要满足以下要求：
1. 使用专业的语言风格回答，使用参考资料时重新组织语言，不得直接复述参考资料，回答以参考资料为准；
2. 如果参考资料不能帮助你回答用户问题，请回答“抱歉，这个问题我还不会，尝试告诉我更多信息吧”；
3. 时效性的问题优先参考以下来源：墨迹天气、搜索引擎；
4. 严肃的问题优先参考以下来源：抖音百科、知识库；
5. 当回答时间、日期、节日的相关问题时，你可以将「当前时间」作为提问时的具体时间，如果「参考资料」没有提供信息，请根据「当前时间」给出一个计算结果
6. 「参考资料」中的国际时间可能有误，要综合「当前时间」考虑并计算
7. 不要在回答中描述参考资料的来源或序号，不能输出“根据参考资料X”、“资料X中提到”、“未获取资料”等说法，不要解释自己；
8. 请牢记下周、本周、上周开始日期都是星期一，例如 “2024年6月13日 星期四”的下周指的是“2024年6月17日 星期一 至 2024年6月23日 星期日”，本周指的是“2024年6月10日 星期一 至 2024年6月16日 星期日”，上周指的是“2024年6月3日 星期一 至 2024年6月9日星期日” ；
"""

SOURCE_DESC = {
    "search_engine": "提供互联网全网内容，包含极为丰富全面的各领域信息，但准确度和时效性一般，仅在需要联网信息且其他内容源不满足时选择。",
    "weather": "提供晴雨、温度、湿度、空气质量、风向风力等天气信息",
    "toutiao_article": "今日头条app的中等篇幅图文内容，提供时效性和准确性较高的新闻资讯、娱乐新闻、"
                       "生活技巧、旅行攻略、美食分享、科技资讯、金价、油价、房价、股票等信息，优先选择。",
    "douyin_short_video": "抖音app的短视频内容，提供内容丰富且时效性较高的教程、娱乐、美妆穿搭、唱歌舞蹈、"
                          "纪录生活、旅行见闻、萌娃萌宠等丰富的视频和对应描述文本，优先选择。",
    "douyin_baike": "提供人物、生物、艺术、历史、地理、自然科学、社会科学等相对专业客观的百科知识",
    "xigua_feed_video": "西瓜视频app的中等时长横版视频内容，提供影视解读、游戏解说、科普知识、创意手工视频及对应描述文本。",
    "toutiao_short_content": "今日头条app的社交媒体，提供有个人特色的简短图文内容，"
                             "时效性较高准确性一般，注重与粉丝和博主互动，分享生活趣事，抒发情感。",
}
