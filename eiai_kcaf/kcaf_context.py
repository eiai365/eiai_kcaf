import enum
import logging
import os

from eiai_kcaf.abc.app_config import ServiceConfig

from eiai_kcaf.kcaf_symptoms import Symptoms

logger = logging.getLogger(f"kcaf.framework.{os.path.splitext(os.path.basename(__file__))[0]}")


class KcafContext:
    symptoms: Symptoms
    kcaf_service_dict: dict
    user_defined_dict: dict
    function: str
    logging_level: str
    output: str
    slack_channel: str
    slack_message_ts: str
    cluster: str
    service: str
    parameters: str

    def __new__(
        cls,
        *,
        symptoms: Symptoms = {},
        kcaf_service_dict: dict = {},
        user_defined_dict: dict = {},
        function: str = None,
        logging_level: str = None,
        output: str = None,
        slack_channel: str = None,
        slack_message_ts: str = None,
        cluster: str = None,
        service: str = None,
        parameters: str = None,
    ):
        self = object.__new__(cls)
        self.symptoms = symptoms
        self.kcaf_service_dict = kcaf_service_dict
        self.user_defined_dict = user_defined_dict
        self.function = function
        self.logging_level = logging_level
        self.output = output
        self.slack_channel = slack_channel
        self.slack_message_ts = slack_message_ts
        self.cluster = cluster
        self.service = service
        self.parameters = parameters
        logger.debug(f'Context created: {", ".join([f"{k}={v}" for k, v in self.__dict__.items()])}')
        return self

    def __getnewargs_ex__(self):
        return (), self.__dict__

    @classmethod
    def init_kcaf(
        cls,
        service_config: ServiceConfig,
        function: str,
        logging_level: str,
        output: str,
        service: str,
        cluster: str,
        parameters: str,
    ) -> "KcafContext":

        service = service
        cluster = cluster

        return cls(
            kcaf_service_dict=service_config.return_kcaf_service_dict(),
            user_defined_dict=service_config.return_user_defined_dict(),
            function=function,
            logging_level=logging_level,
            output=output,
            slack_channel=service_config.get_slack_channel_for_service(service),
            service=service,
            cluster=cluster,
            parameters=parameters,
        )
