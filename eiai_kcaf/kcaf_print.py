from contextlib import contextmanager
from logging import Logger
import typing

from eiai_kcaf.kcaf_context import KcafContext
from eiai_kcaf import kcaf_slack


class KcafPrintBuffer:
    header: str
    messages: typing.Sequence[str]

    def __init__(self, header: str):
        self.header = header
        self.messages = []

    def print(self, message: str):
        self.messages.append(message)

    def flush(self, context: KcafContext, logger: Logger):
        if context.output == 'local' or context.output is None:
            logger.info(f"======== {self.header} ========")
            for message in self.messages:
                logger.info(message)
        if context.output == 'slack':
            logger.info(f'{{"header": "{self.header}", "messages": {self.messages}}}')
            expanded_message = "\n".join(self.messages)
            kcaf_slack.post_message_thread(channel=context.slack_channel, text=f"{self.header}\n```\n{expanded_message}\n```", thread_ts=context.slack_message_ts, )


@contextmanager
def kcaf_print_buf(header: str, context: KcafContext, logger: Logger) -> KcafPrintBuffer:
    buffer = KcafPrintBuffer(header)
    yield buffer
    buffer.flush(context, logger)
