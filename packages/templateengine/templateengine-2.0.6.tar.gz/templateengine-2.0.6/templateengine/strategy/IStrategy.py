from abc import ABC, abstractmethod
from ..data.InputParams import InputParams
from .IGoal import IGoal
from ..plan.IPlanner import IPlanner
from ..ai.IModel import IModel
from ..exec.IExecutor import IExecutor

class IStrategy(ABC):
    @abstractmethod
    def __init__(self):
        self.goals: list[IGoal] = []
        self.params: InputParams = None
        self.executor: IExecutor = None
        self.ai_model: IModel = None
        self.planner: IPlanner = None
        self.tools: list[str] = []
        self.metadata: dict = None

    @abstractmethod
    def set_params(self, params: InputParams) -> None:
        pass

    @abstractmethod
    def set_goals(self) -> None:
        pass

    @abstractmethod
    def set_metadata(self, metadata: dict) -> None:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def run(self) -> None:        
        pass
