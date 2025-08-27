import ssl
import time
import hmac
import hashlib
import os
import typing

from slack_sdk import WebClient
from slack_sdk.models.blocks.blocks import Block

from ratelimit import limits, RateLimitException
from backoff import on_exception, expo

PERIOD = 60  # seconds
MAX_CALLS_PER_MINUTE = 50

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = None


def get_client():
    global client

    if client is None:
        client = WebClient(token=os.environ["EIAI_KCAF_SLACK_TOKEN"], ssl=ssl_context, timeout=300)
    return client


@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=MAX_CALLS_PER_MINUTE, period=PERIOD)
def post_message(*, channel: str, text: str, blocks: typing.Sequence[typing.Union[typing.Dict, Block]] = None) -> str:
    if blocks is None:
        if len(text) < 4000:
            result = get_client().chat_postMessage(channel=channel, text=text)
        else:
            result = get_client().files_upload(channel=channel, content=text)
    else:
        result = get_client().chat_postMessage(channel=channel, blocks=blocks, text=text)

    message_ts = result.data.get("ts")
    return message_ts


@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=MAX_CALLS_PER_MINUTE, period=PERIOD)
def post_message_thread(
    *, channel: str, text: str, thread_ts: str, blocks: typing.Sequence[typing.Union[typing.Dict, Block]] = None
) -> None:
    if blocks is None:
        if len(text) < 4000:
            get_client().chat_postMessage(channel=channel, thread_ts=thread_ts, text=text)
        else:
            get_client().files_upload(channels=channel, thread_ts=thread_ts, content=text)
    else:
        get_client().chat_postMessage(channel=channel, thread_ts=thread_ts, blocks=blocks, text=text)


def update_message(
    *,
    channel: str,
    thread_ts: str,
    text: str,
    blocks: typing.Sequence[typing.Union[typing.Dict, Block]] = None,
) -> None:
    if blocks is None:
        if len(text) < 4000:
            result = get_client().chat_update(channel=channel, text=text, ts=thread_ts)
        else:
            result = get_client().files_upload(channel=channel, content=text, ts=thread_ts)
    else:
        result = get_client().chat_update(channel=channel, blocks=blocks, text=text, ts=thread_ts)

    thread_ts = result.data.get("ts")


def upload_file(*, channel: str, file: str, thread_ts: str, title: str = None) -> None:
    get_client().files_upload_v2(channel=channel, thread_ts=thread_ts, file=file, title=title)


def users_lookup_by_email(*, email: str) -> typing.Dict:
    return get_client().users_lookupByEmail(email=email)


def retrieve_message(*, channel: str, inclusive: bool = True, slack_message_ts: str) -> str:
    result = get_client().conversations_history(channel=channel, inclusive=inclusive, oldest=slack_message_ts, limit=1)
    message = result["messages"][0]["blocks"][0]["text"]["text"]
    return message


def get_email_for_user(*, user_id: str) -> str:
    result = get_client().users_info(user=user_id)
    email = result.get("user").get("profile").get("email")
    return email


def modal_dialog(*, dialog: typing.Sequence[typing.Union[typing.Dict, Block]], trigger_id: str) -> str:
    return get_client().dialog_open(dialog=dialog, trigger_id=trigger_id)


def get_chat_link(*, channel: str, message_ts: str) -> str:
    result = get_client().chat_getPermalink(channel=channel, message_ts=message_ts)
    return result["permalink"]


def validate_hmac(timestamp: str, slack_signature: str, payload: str) -> bool:
    if abs(time.time() - float(timestamp)) > 60 * 5:
        return False

    sig_basestring = str.encode("v0:" + str(timestamp) + ":") + payload
    request_hash = (
        "v0=" + hmac.new(str.encode(os.environ.get("EIAI_KCAF_SLACK_SIGNING_SECRET")), sig_basestring, hashlib.sha256).hexdigest()
    )
    return hmac.compare_digest(request_hash, slack_signature)
