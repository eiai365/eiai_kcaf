#!/usr/bin/env python3

"""
KCAF API.
Developer: Kevin Cao
email: kevincao@au1.ibn.com
Slack: @kevincao
Date: August 2025
"""

import os
from argparse import ArgumentParser
import logging.config

from eiai_kcaf.base_processor import ProcessorExitCode
from eiai_kcaf.processor_runner import ProcessorRunner
import eiai_kcaf.kcaf_cli
from eiai_kcaf.kcaf_package import KcafConfig

from eiai_kcaf.kcaf_config import KcafClusterConfig, KcafServiceConfig

logger = logging.getLogger(f"kcaf.framework.{os.path.splitext(os.path.basename(__file__))[0]}")


class KcafAPI:

    @staticmethod
    def run_kcaf_api(function=None, service=None, environment=None, parameters=None, output=None, logging_level=None):
        
        kcaf_service = eiai_kcaf.kcaf_cli.KcafCLI(KcafServiceConfig(), KcafClusterConfig(), KcafConfig(), ProcessorRunner())

        parser = ArgumentParser()

        parser.add_argument("kcaf_bus")
        parser.add_argument("function")
        parser.add_argument("service")
        parser.add_argument("environment")
        parser.add_argument("parameters")
        parser.add_argument("logging_level")
        parser.add_argument("output")

        args = parser.parse_args(["kcaf_bus", function, service, environment, parameters, logging_level, output])
        kcaf_service.run(args)

        return ProcessorExitCode.EXIT_CODE_PROCESSOR_SUCCESS
