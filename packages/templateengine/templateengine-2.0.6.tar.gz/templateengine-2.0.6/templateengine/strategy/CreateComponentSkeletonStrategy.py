import time
from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.refer import IReferenceable, IReferences, DependencyResolver, Descriptor

from ..data.InputParams import InputParams
from ..strategy.CommonStrategy import CommonStrategy
from ..strategy.Goal import Goal
from ..exec.tools.ToolTypes import ToolTypes

class CreateComponentSkeletonStrategy(CommonStrategy):
    _dependencyResolver: DependencyResolver = None
    params: InputParams = None

    def __init__(self):
        super().__init__()
        self._dependencyResolver.put("planner", Descriptor("templateengine-v2", "planner", "*", "create-skeleton", "1.0"))
        # self._dependencyResolver.put("ai-model", Descriptor("templateengine-v2", "ai-model", "*", "*", "1.0"))
        self.tools = [ToolTypes.COPY_DIR, ToolTypes.CREATE_DIR, ToolTypes.RENAME_DIR, ToolTypes.DELETE_DIR,
                           ToolTypes.COPY_FILE, ToolTypes.CREATE_FILE, ToolTypes.RENAME_FILE, ToolTypes.DELETE_FILE,
                           ToolTypes.EDIT_CONTENT, ToolTypes.COPY_ALL]
        # define goals
        self.set_goals()

    def set_goals(self):
        goal = Goal()
        goal.set(self.params, 
                 (f"Create a component skeleton from the template. \n"
                  "Using the search and replace array obtained from the parameters, use it to find any occurrence of the directory name, file name, and file content and then replace.\n"
                  "Using the list of tools to achieve the goals.\n"))
        self.goals = [goal]

    def get_name(self) -> str:
        return "create-skeleton"