from abc import ABC, abstractmethod
from ..data.InputParams import InputParams
from ..strategy.GoalType import GoalType

class IGoal(ABC):
    @abstractmethod
    def __init__(self):
        self.type = GoalType.Unknown
        self.params = None
        self.goal = None
    
    @abstractmethod
    def set_params(self, params: InputParams) -> None:
        pass

    @abstractmethod
    def set_goal(self, goal: str) -> None:
        pass

    @abstractmethod
    def set(self, params: InputParams, goal: str) -> None:
        pass

    @abstractmethod
    def get_goal(self) -> str:
        pass
