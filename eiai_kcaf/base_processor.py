from abc import abstractmethod
import enum
import logging
import os
import traceback
from datetime import datetime
from typing import NamedTuple, Union, Any, Literal

from eiai_kcaf.kcaf_context import KcafContext
from eiai_kcaf import kcaf_slack

logger = logging.getLogger(f"kcaf.framework.{os.path.splitext(os.path.basename(__file__))[0]}")


class ProcessorExitCode(enum.Enum):
    EXIT_CODE_PROCESSOR_DOES_NOT_MATCH = enum.auto()
    EXIT_CODE_PROCESSOR_SUCCESS = enum.auto()
    EXIT_CODE_PROCESSOR_ERROR = enum.auto()
    EXIT_CODE_PROCESSOR_NONEXISTENT = enum.auto()


class ProcessorReturnValues(NamedTuple):
    first_error: datetime
    last_error: datetime
    processor_exit_code: ProcessorExitCode


class BaseProcessor:
    name: str

    def __init__(self, name):
        self.name = name

    @staticmethod
    def save_data(context: KcafContext, data: object, name: str) -> None:
        context.symptoms[name] = data

    @staticmethod
    def center_text(text) -> str:
        terminal_size = os.get_terminal_size()
        width = terminal_size.columns
        text_length = len(text)
        space = (width - text_length) // 2
        centered_text = ' ' * space + text
        return centered_text

    @staticmethod
    def open_slack_thread(context: KcafContext) -> str:
        message = (f"{context.cluster.upper()} `{context.function}` \n"
                   f"{context.service}"
                   )

        return kcaf_slack.post_message(channel=context.slack_channel, text=message, )

    @staticmethod
    def update_slack_thread(context: KcafContext) -> None:
        message = kcaf_slack.retrieve_message(
            channel=context.slack_channel, slack_message_ts=context.slack_message_ts
        )
        kcaf_slack.update_message(channel=context.slack_channel, text=message, thread_ts=context.slack_message_ts, )

    def run(self, context: KcafContext) -> Literal[
                                               ProcessorExitCode.EXIT_CODE_PROCESSOR_DOES_NOT_MATCH, ProcessorExitCode.EXIT_CODE_PROCESSOR_ERROR, ProcessorExitCode.EXIT_CODE_PROCESSOR_SUCCESS] | None | ProcessorExitCode | ProcessorReturnValues | Any:
        try:
            if not self._is_processor_match(context):
                return ProcessorExitCode.EXIT_CODE_PROCESSOR_DOES_NOT_MATCH
            logger.info(f"\n\n"
                        f"{self.center_text('+-----------------------------------------------------------+')}\n"
                        f"{self.center_text('|                                                           |')}\n"
                        f"{self.center_text('|          Kubernetes Cluster Automation Framework          |')}\n"
                        f"{self.center_text('|          =======================================          |')}\n"
                        f"{self.center_text('|                                                           |')}\n"
                        f"{self.center_text('+-----------------------------------------------------------+')}\n"
                        f"\n"
                        f"{self.center_text(f'<<<<<<<<<  Function: {context.function}  >>>>>>>>>')}\n"
                        f"\n\n")

            if context.output == 'slack':
                if os.environ.get('EIAI_KCAF_SLACK_TOKEN') is None or os.environ.get('EIAI_KCAF_SLACK_TOKEN') == '':
                    logger.error(f"Output to slack is not supported because Environment Variable EIAI_KCAF_SLACK_TOKEN is not configured, slack output is ignored.")
                    context.output = 'local'
                else:
                    if (os.environ.get('EIAI_KCAF_DEFAULT_SLACK_CHANNEL') is None or os.environ.get('EIAI_KCAF_DEFAULT_SLACK_CHANNEL') == '') and (os.environ.get('EIAI_KCAF_SERVICE_CONFIG_LOCATION') is None or os.environ.get('EIAI_KCAF_SERVICE_CONFIG_LOCATION') == ''):
                        logger.error(f"Service is not configured with a slack channel, slack output is ignored. If you want slack output, please setup Environment Variable EIAI_KCAF_DEFAULT_SLACK_CHANNEL or service config json file.")
                        context.output = 'local'
                    else:
                        context.slack_message_ts = self.open_slack_thread(context)

            return_values = self._run(context)

            if return_values is None:
                return ProcessorExitCode.EXIT_CODE_PROCESSOR_SUCCESS
            elif type(return_values) is ProcessorExitCode:
                return return_values
            elif type(return_values) is ProcessorReturnValues:
                return return_values.get("processor_exit_code", ProcessorExitCode.EXIT_CODE_PROCESSOR_SUCCESS)
        except Exception:
            logger.error(f"Processor exited with following exception: {traceback.format_exc()}")
            return ProcessorExitCode.EXIT_CODE_PROCESSOR_ERROR

    @abstractmethod
    def _get_help_text(self) -> str:
        return "No help text is provided for this function..."

    @abstractmethod
    def _is_processor_match(self, context: KcafContext) -> bool:
        raise NotImplementedError("_is_match() must be implemented in each subclass of BaseProcessor")

    @abstractmethod
    def _run(self, context: KcafContext) -> Union[ProcessorExitCode, ProcessorReturnValues]:
        raise NotImplementedError("_run() must be implemented in each subclass of BaseProcessor")
