from typing import Callable, Any, Union, List, Pattern, Coroutine

import tgram
import re
import inspect


class Filter:
    def __init__(self, filter_: Union[Callable, Coroutine]) -> None:
        self._filter = filter_

    async def __call__(self, bot: "tgram.TgBot", update: Any) -> bool:
        if inspect.iscoroutinefunction(self._filter):
            r = await self._filter(bot, update)
        else:
            r = await bot.loop.run_in_executor(bot.executor, self._filter, bot, update)

        return bool(r)

    def __invert__(self) -> "Filter":
        async def func(*args):
            return not await self(*args)

        return Filter(func)

    def __and__(self, other: "Filter") -> "Filter":
        async def func(*args):
            return await self(*args) and await other(*args)

        return Filter(func)

    def __or__(self, other: "Filter") -> "Filter":
        async def func(*args):
            return await self(*args) or await other(*args)

        return Filter(func)


all = Filter(lambda _, __: True)
threaded = Filter(lambda _, m: getattr(m, "message_thread_id"))
from_user = Filter(lambda _, m: getattr(m, "from_user"))
sender_chat = Filter(lambda _, m: getattr(m, "sender_chat"))
business_connection_id = Filter(lambda _, m: getattr(m, "business_connection_id"))
forward = Filter(lambda _, m: getattr(m, "forward_origin"))
topic_message = Filter(lambda _, m: getattr(m, "is_topic_message"))
automatic_forward = Filter(lambda _, m: getattr(m, "is_automatic_forward"))
reply = Filter(lambda _, m: getattr(m, "reply_to_message"))
quote = Filter(lambda _, m: getattr(m, "quote"))
reply_to_story = Filter(lambda _, m: getattr(m, "reply_to_story"))
via_bot = Filter(lambda _, m: getattr(m, "via_bot"))
protected_content = Filter(lambda _, m: getattr(m, "has_protected_content"))
from_offline = Filter(lambda _, m: getattr(m, "is_from_offline"))
media_group = Filter(lambda _, m: getattr(m, "media_group_id"))
text = Filter(lambda _, m: getattr(m, "text"))
entities = Filter(lambda _, m: getattr(m, "entities"))
effected_message = Filter(lambda _, m: getattr(m, "effect_id"))
animation = Filter(lambda _, m: getattr(m, "animation"))
audio = Filter(lambda _, m: getattr(m, "audio"))
document = Filter(lambda _, m: getattr(m, "document"))
photo = Filter(lambda _, m: getattr(m, "photo"))
sticker = Filter(lambda _, m: getattr(m, "sticker"))
story = Filter(lambda _, m: getattr(m, "story"))
video = Filter(lambda _, m: getattr(m, "video"))
video_note = Filter(lambda _, m: getattr(m, "video_note"))
voice = Filter(lambda _, m: getattr(m, "voice"))
caption = Filter(lambda _, m: getattr(m, "caption"))
media_spoiler = Filter(lambda _, m: getattr(m, "has_media_spoiler"))
contact = Filter(lambda _, m: getattr(m, "contact"))
dice = Filter(lambda _, m: getattr(m, "dice"))
game = Filter(lambda _, m: getattr(m, "game"))
poll = Filter(lambda _, m: getattr(m, "poll"))
venue = Filter(lambda _, m: getattr(m, "venue"))
location = Filter(lambda _, m: getattr(m, "location"))
new_chat_members = Filter(lambda _, m: getattr(m, "new_chat_members"))
left_chat_member = Filter(lambda _, m: getattr(m, "left_chat_member"))
new_chat_title = Filter(lambda _, m: getattr(m, "new_chat_title"))
new_chat_photo = Filter(lambda _, m: getattr(m, "new_chat_photo"))
delete_chat_photo = Filter(lambda _, m: getattr(m, "delete_chat_photo"))
group_chat_created = Filter(lambda _, m: getattr(m, "group_chat_created"))
supergroup_chat_created = Filter(lambda _, m: getattr(m, "supergroup_chat_created"))
channel_chat_created = Filter(lambda _, m: getattr(m, "channel_chat_created"))
message_auto_delete_timer_changed = Filter(
    lambda _, m: getattr(m, "message_auto_delete_timer_changed")
)
migrate_to_chat_id = Filter(lambda _, m: getattr(m, "migrate_to_chat_id"))
migrate_from_chat_id = Filter(lambda _, m: getattr(m, "migrate_from_chat_id"))
pinned_message = Filter(lambda _, m: getattr(m, "pinned_message"))
invoice = Filter(lambda _, m: getattr(m, "invoice"))
successful_payment = Filter(lambda _, m: getattr(m, "successful_payment"))
refunded_payment = Filter(lambda _, m: getattr(m, "refunded_payment"))
users_shared = Filter(lambda _, m: getattr(m, "users_shared"))
chat_shared = Filter(lambda _, m: getattr(m, "chat_shared"))
connected_website = Filter(lambda _, m: getattr(m, "connected_website"))
write_access_allowed = Filter(lambda _, m: getattr(m, "write_access_allowed"))
passport_data = Filter(lambda _, m: getattr(m, "passport_data"))
proximity_alert_triggered = Filter(lambda _, m: getattr(m, "proximity_alert_triggered"))
boost_added = Filter(lambda _, m: getattr(m, "boost_added"))
chat_background_set = Filter(lambda _, m: getattr(m, "chat_background_set"))
forum_topic_created = Filter(lambda _, m: getattr(m, "forum_topic_created"))
forum_topic_edited = Filter(lambda _, m: getattr(m, "forum_topic_edited"))
forum_topic_closed = Filter(lambda _, m: getattr(m, "forum_topic_closed"))
forum_topic_reopened = Filter(lambda _, m: getattr(m, "forum_topic_reopened"))
general_forum_topic_hidden = Filter(
    lambda _, m: getattr(m, "general_forum_topic_hidden")
)
general_forum_topic_unhidden = Filter(
    lambda _, m: getattr(m, "general_forum_topic_unhidden")
)
giveaway_created = Filter(lambda _, m: getattr(m, "giveaway_created"))
giveaway = Filter(lambda _, m: getattr(m, "giveaway"))
giveaway_winners = Filter(lambda _, m: getattr(m, "giveaway_winners"))
giveaway_completed = Filter(lambda _, m: getattr(m, "giveaway_completed"))
video_chat_scheduled = Filter(lambda _, m: getattr(m, "video_chat_scheduled"))
video_chat_started = Filter(lambda _, m: getattr(m, "video_chat_started"))
video_chat_ended = Filter(lambda _, m: getattr(m, "video_chat_ended"))
video_chat_participants_invited = Filter(
    lambda _, m: getattr(m, "video_chat_participants_invited")
)
web_app_data = Filter(lambda _, m: getattr(m, "web_app_data"))
reply_markup = Filter(lambda _, m: getattr(m, "reply_markup"))

service = Filter(lambda _, m: isinstance(m, tgram.types.Message) and m.service)

media = Filter(lambda _, m: isinstance(m, tgram.types.Message) and m.media)


def sender(ids: Union[str, int, List[Union[str, int]]]) -> Filter:
    """Filter messages coming from one or more sender chat"""
    ids = (
        {ids.lower() if isinstance(ids, str) else ids}
        if not isinstance(ids, list)
        else {i.lower() if isinstance(i, str) else i for i in ids}
    )

    return Filter(
        lambda _, m: getattr(m, "sender_chat")
        and (
            m.sender_chat.id in ids
            or (m.sender_chat.username and m.sender_chat.username.lower() in ids)
        )
    )


def user(ids: Union[str, int, List[Union[str, int]]]) -> Filter:
    """Filter messages coming from one or more users"""
    ids = (
        {ids.lower() if isinstance(ids, str) else ids}
        if not isinstance(ids, list)
        else {i.lower() if isinstance(i, str) else i for i in ids}
    )

    return Filter(
        lambda _, m: getattr(m, "from_user")
        and (
            m.from_user.id in ids
            or (m.from_user.username and m.from_user.username.lower() in ids)
        )
    )


def chat(ids: Union[str, int, List[Union[str, int]]]) -> Filter:
    """Filter messages coming from one or more chats"""
    ids = (
        {ids.lower() if isinstance(ids, str) else ids}
        if not isinstance(ids, list)
        else {i.lower() if isinstance(i, str) else i for i in ids}
    )

    return Filter(
        lambda _, m: getattr(m, "chat")
        and (m.chat.id in ids or (m.chat.username and m.chat.username.lower() in ids))
    )


def regex(pattern: Union[str, Pattern], flags: int = 0):
    """Filter updates that match a given regular expression pattern."""
    compiler = pattern if isinstance(pattern, Pattern) else re.compile(pattern, flags)

    async def regex_filter(_, m):
        if not isinstance(
            m,
            (
                tgram.types.Message,
                tgram.types.CallbackQuery,
                tgram.types.InlineQuery,
                tgram.types.PreCheckoutQuery,
            ),
        ):
            raise ValueError(f"Regex filter doesn't work with {m.__class__.__name__}")

        value = (
            (m.text or m.caption)
            if isinstance(m, tgram.types.Message)
            else m.data
            if isinstance(m, tgram.types.CallbackQuery)
            else m.query
            if isinstance(m, tgram.types.InlineQuery)
            else m.invoice_payload
            if isinstance(m, tgram.types.PreCheckoutQuery)
            else None
        )

        if value is None:
            return False

        m.matches = list(compiler.finditer(value)) or None

        return bool(m.matches)

    return Filter(regex_filter)


def chat_type(types: Union[list, str]) -> Filter:
    """Filter updates that match a given chat type."""
    types = (
        {types.lower()} if not isinstance(types, list) else {i.lower() for i in types}
    )

    async def chat_filter(_, m):
        if isinstance(m, tgram.types.CallbackQuery) and m.message and m.message.chat:
            chat_type = m.message.chat.type
        elif isinstance(m, tgram.types.InlineQuery):
            chat_type = m.chat_type
        elif getattr(m, "chat"):  # Most of other updates types have chat attribute.
            chat_type = m.chat.type
        else:
            raise ValueError(
                f"Chat type filter doesn't work with {m.__class__.__name__}"
            )

        return bool(chat_type in types)

    return Filter(chat_filter)


private = chat_type("private")
group = chat_type(["group", "supergroup"])


def command(
    commands: Union[str, List[str]],
    prefixes: Union[str, List[str]] = "/",
    case_sensitive: bool = False,
) -> Filter:
    """Filter commands, i.e.: text messages starting with "/" or any other custom prefix."""
    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}

    prefixes = [] if prefixes is None else prefixes
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {""}
    command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def filter_fucn(b: "tgram.TgBot", m: "tgram.types.Message"):
        text = m.text or m.caption
        username = b.me.username

        if text is None:
            return False

        for prefix in prefixes:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix) :]

            for cmd in commands:
                if not re.match(
                    rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)",
                    without_prefix,
                    flags=re.IGNORECASE if not case_sensitive else 0,
                ):
                    continue

                without_command = re.sub(
                    rf"{cmd}(?:@?{username})?\s?",
                    "",
                    without_prefix,
                    count=1,
                    flags=re.IGNORECASE if not case_sensitive else 0,
                )

                m.command = [cmd] + [
                    re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                    for m in command_re.finditer(without_command)
                ]

                return True

        return False

    return Filter(filter_fucn)
