import os

from eiai_kcaf.kcaf_context import KcafContext
from eiai_kcaf import kcaf_logging


class KcafLog:

    def setup_kcaf_product_service_log(self, context: KcafContext, base_name):
        service_config_dict = context.kcaf_service_dict
        log_path = self.get_log_path()
        log = kcaf_logging.setup_kcaf_product_service_logging(service_config_dict, context.service, base_name, context.logging_level, str(log_path))

        return log

    def setup_kcaf_server_service_log(self, service_name, base_name, log_level):
        log_path = self.get_log_path()
        log = kcaf_logging.setup_kcaf_server_service_logging(service_name, base_name, log_level, str(log_path))

        return log

    @staticmethod
    def get_log_path():
        if os.environ.get('KCAF_LOG_DIR') is not None and os.environ.get('KCAF_LOG_DIR') != '' and os.path.exists(
                os.environ.get('KCAF_LOG_DIR')):
            log_path = os.environ.get('KCAF_LOG_DIR')
        else:
            log_path = os.path.abspath(os.path.join(os.getcwd())) + "/log/"
        if os.path.exists(log_path) and os.path.isdir(log_path):
            pass
        else:
            os.makedirs(log_path)

        return log_path
