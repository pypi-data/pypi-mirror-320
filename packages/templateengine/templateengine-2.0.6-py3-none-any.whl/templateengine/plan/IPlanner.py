from abc import ABC, abstractmethod
from ..data.InputParams import InputParams
from ..strategy.IGoal import IGoal
from ..exec.tools.ITool import ITool
from ..ai.IModel import IModel
from ..exec.Action import Action
from ..strategy.StrategyAction import StrategyAction

class IPlanner(ABC):
    @abstractmethod
    def __init__(self):
        self.params: InputParams = None
        self.goals: list[IGoal] = []
        self.tools: dict = {}
        self.ai_model: IModel = None
        self.metadata: dict = {}

    @abstractmethod
    def set_params(self, params: InputParams) -> None:
        pass

    @abstractmethod
    def set_goals(self, goals: list[IGoal]) -> None:
        pass

    @abstractmethod
    def set_tools(self, tools: dict) -> None:
        pass

    @abstractmethod
    def set_model(self, ai_model: IModel) -> None:
        pass

    @abstractmethod
    def set_metadata(self, metadata: dict) -> None:
        pass    

    @abstractmethod
    def set(self, params: InputParams, goals: list[IGoal], tools: dict, ai_model: IModel, metadata: dict) -> None:
        pass

    @abstractmethod
    def run(self) -> list[Action] | list[StrategyAction]:
        pass