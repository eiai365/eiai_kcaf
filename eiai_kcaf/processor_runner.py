import importlib

import logging

import os
from eiai_kcaf.abc.processor_activation_controller import ProcessorActivationController

from eiai_kcaf.base_processor import ProcessorExitCode
from eiai_kcaf.kcaf_context import KcafContext
import importlib.resources

from eiai_kcaf.kcaf_package import KcafConfig

logger = logging.getLogger(f"kcaf.framework.{os.path.splitext(os.path.basename(__file__))[0]}")


class ProcessorRunner:
    processor_activation_controller: ProcessorActivationController

    def __init__(self, processor_activation_controller: ProcessorActivationController = None):
        self.processor_activation_controller = processor_activation_controller

    @staticmethod
    def specify_and_run_processor(context: KcafContext, kcaf_config: KcafConfig):
        function_processor = f"{context.function.lower()}"

        if not os.path.exists(f"{kcaf_config.processors_package}/{function_processor}.py"):
            logger.error(f"{function_processor} is non-existent.")
            return ProcessorExitCode.EXIT_CODE_PROCESSOR_NONEXISTENT
        module = importlib.import_module(f"{kcaf_config.processors_package}.{function_processor}", package=None)
        processor = module.ConcreteProcessor(function_processor)

        processor.run(context)
        return ProcessorExitCode.EXIT_CODE_PROCESSOR_SUCCESS

    def select_and_run_processor(self, context: KcafContext, kcaf_config: KcafConfig):
        processor_modules = importlib.resources.files(kcaf_config.processors_package)

        for processor_module in sorted(processor_modules.iterdir(), key=lambda _module: _module.name):
            if (
                processor_module.is_dir()
                or processor_module.name == "__init__.py"
                or os.path.splitext(processor_module.name)[-1] != ".py"
            ):
                continue

            if (
                self.processor_activation_controller is not None
                and not self.processor_activation_controller.is_processor_active(processor_module.stem)
            ):
                logger.debug(f"Processor is not active: {processor_module.stem}")
                continue

            module = importlib.import_module(f"{kcaf_config.processors_package}.{processor_module.stem}")
            if (
                module.ConcreteProcessor(processor_module.name).run(context)
                != ProcessorExitCode.EXIT_CODE_PROCESSOR_DOES_NOT_MATCH
            ):
                break
            else:
                logger.debug(f"Processor does not match: {processor_module.stem}")
                continue
        else:
            logger.info(f"No processor is available for this function {context.function}.")
