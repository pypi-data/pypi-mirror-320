from abc import ABC, abstractmethod
from ..data.InputParams import InputParams
from .tools.ITool import ITool
from .Action import Action

class IExecutor(ABC):
    @abstractmethod
    def __init__(self):
        self.params: InputParams = None
        self.tools: list[ITool] = []       

    @abstractmethod
    def get_tool_promt(self, tool_name: str) -> str:
        pass

    @abstractmethod
    def run(self, params: InputParams, actions: list[Action]) -> None:
        pass

    @abstractmethod
    def validate(self, params: InputParams, actions: list[Action]) -> None:
        pass    