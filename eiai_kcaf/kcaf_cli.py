#!/usr/bin/env python3

"""
Local script runner.
"""
from argparse import Namespace
import os
import logging.config

from eiai_kcaf.processor_runner import ProcessorRunner
from eiai_kcaf.kcaf_context import KcafContext
from eiai_kcaf.abc.app_config import ClusterConfig, ServiceConfig
from eiai_kcaf.kcaf_package import KcafConfig

logger = logging.getLogger(f"kcaf.framework.{os.path.splitext(os.path.basename(__file__))[0]}")


class KcafCLI:
    service_config: ServiceConfig
    cluster_config: ClusterConfig
    kcaf_config: KcafConfig
    processor_runner: ProcessorRunner

    def __init__(
        self,
        service_config: ServiceConfig,
        cluster_config: ClusterConfig,
        kcaf_config: KcafConfig,
        processor_runner: ProcessorRunner,
    ):
        self.service_config = service_config
        self.cluster_config = cluster_config
        self.kcaf_config = kcaf_config
        self.processor_runner = processor_runner

    def run(self, args: Namespace):
        if args.kcaf_bus == "kcaf_bus":
            context = KcafContext.init_for_kcaf_bus(
                bus=args.kcaf_bus,
                service_config=self.service_config,
                function=args.function,
                logging_level=args.logging_level,
                output=args.output,
                cluster=args.environment.replace('-', '_'),
                service=args.service,
                parameters=args.parameters,
                )
            self.cluster_config.switch_cluster(context.cluster)
            self.processor_runner.select_and_run_processor(context, self.kcaf_config)
        else:
            logger.error(f"EIAI only support kcaf_bus, nothing else.")
            exit(110)
