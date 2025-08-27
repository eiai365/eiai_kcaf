import os


class KcafConfig:
    processors_package: str

    def __init__(self):
        processors_package = os.environ.get('EIAI_ KCAF_PROCESSORS_PACKAGE')
        if processors_package is not None and processors_package != '':
            self.processors_package = processors_package
        else:
            self.processors_package = 'kcaf_cli'
