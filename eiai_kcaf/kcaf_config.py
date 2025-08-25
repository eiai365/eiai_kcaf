import os
import json
import logging.config

from eiai_kcaf.abc.app_config import ClusterConfig, ClusterEnum, ServiceEnum, ServiceConfig

logger = logging.getLogger(f"kcaf.framework.{os.path.splitext(os.path.basename(__file__))[0]}")


class KcafClusterConfig(ClusterConfig):
    def switch_cluster(self, cluster: ClusterEnum):
        if cluster not in ['unknown', 'none']:
            kubeconfig_prefix = os.environ["KCAF_KUBECONFIG_PREFIX"]
            config = json.loads(os.environ["KCAF_CLUSTER_KUBECONFIG"])
            os.environ["KUBECONFIG"] = os.path.expandvars(kubeconfig_prefix + config[cluster]["KUBECONFIG"])


class KcafServiceConfig(ServiceConfig):
    def __init__(self):
        kcaf_logging_config = '{"version": 1,"handlers": {"console_processor": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout"}},"loggers": {"kcaf": {"level": "INFO", "handlers": ["console_processor"]}}}'
        logging.config.dictConfig(json.loads(kcaf_logging_config))

        product_logging_config = os.environ.get('KCAF_PRODUCT_LOGGING_CONFIG_LOCATION')
        if product_logging_config is not None and product_logging_config != '':
            with open(product_logging_config, "r") as product_logging_config_f:
                product_logging_config = json.load(product_logging_config_f)
                logging.config.dictConfig(product_logging_config)

        kcaf_service_config = os.environ.get('KCAF_SERVICE_CONFIG_LOCATION')
        if kcaf_service_config is None or kcaf_service_config == '':
            defautl_slack_channel = os.environ.get('KCAF_DEFAULT_SLACK_CHANNEL')
            if defautl_slack_channel is None or defautl_slack_channel == '':
                # logger.error(f"Environment Variable KCAF_DEFAULT_SLACK_CHANNEL is not configured")
                defautl_slack_channel = ''
            kcaf_service_json_str = '{"service": {"generic": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},' + '"unknown": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},' + '"none": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},'
            kcaf_services = os.environ.get("KCAF_SERVICES")
            if kcaf_services is not None and kcaf_services != '':
                for service in os.environ.get("KCAF_SERVICES").split(','):
                    kcaf_service_json_str = kcaf_service_json_str + f'"{service}": ' + '{"slack_channel": ' + f'"{defautl_slack_channel}"' + '},'
            kcaf_service_json_str = kcaf_service_json_str.rstrip(kcaf_service_json_str[-1]) + '},"logging_level": "WARNING"}'
            # else:
                # kcaf_service_json_str = '{"service": {"assistant": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},"discovery": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},"speech": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},"nlu": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},"rbr": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},"wks": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},"generic": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},"unknown": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '},"none": {"slack_channel": ' + f'"{defautl_slack_channel}"' + '}},"logging_level": "WARNING"}'
            self.kcaf_service_config_dict = json.loads(kcaf_service_json_str)
        else:
            with open(kcaf_service_config) as kcaf_config_f:
                self.kcaf_service_config_dict = json.load(kcaf_config_f)

        user_defined_config = os.environ.get('KCAF_USER_DEFINED_CONFIG_LOCATION')
        if user_defined_config is None or user_defined_config == '':
            kcaf_user_defined = '{}'
            self.user_defined_config_dict = json.loads(kcaf_user_defined)
        else:
            with open(user_defined_config) as user_config_f:
                self.user_defined_config_dict = json.load(user_config_f)

    def get_slack_channel_for_service(self, service: ServiceEnum) -> str:
        return self.kcaf_service_config_dict["service"][service]["slack_channel"]

    def return_kcaf_service_dict(self) -> dict:
        return self.kcaf_service_config_dict

    def return_user_defined_dict(self) -> dict:
        return self.user_defined_config_dict
