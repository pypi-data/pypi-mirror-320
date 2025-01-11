from abc import ABC, abstractmethod
from ...data.InputParams import InputParams

class ITool(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_params(self, params: InputParams) -> None:
        pass

    @abstractmethod
    def get_promt(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def run(self, tool_params) -> None:
        pass

    @abstractmethod
    def validate(self, tool_params) -> None:
        pass