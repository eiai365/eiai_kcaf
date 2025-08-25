from abc import abstractmethod


class ProcessorActivationController:
    @abstractmethod
    def is_processor_active(self, processor_name: str) -> bool:
        raise NotImplementedError()
