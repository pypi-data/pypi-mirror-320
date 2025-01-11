from ..data.InputParams import InputParams
from .GoalType import GoalType
from .IGoal import IGoal

class Goal(IGoal):
    def __init__(self):
        pass

    def set_params(self, params: InputParams) -> None:
        self.params = params

    def set_goal(self, goal: str) -> None:
        self.goal = goal

    def set(self, params: InputParams, goal: str) -> None:
        self.params = params
        self.goal = goal

    def get_goal(self) -> str:
        return self.goal