from pip_services4_observability.log import CompositeLogger
from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.refer import IReferenceable, IReferences, DependencyResolver, Descriptor

from tqdm import tqdm
from ..plan.IPlanner import IPlanner
from ..data.InputParams import InputParams
from ..strategy.IGoal import IGoal
from ..ai.IModel import IModel
from ..data.ICustomSpinner import ICustomSpinner


class CommonPlanner(IPlanner, IConfigurable, IReferenceable):
    _dependencyResolver: DependencyResolver = None
    logger: CompositeLogger = None
    verbose: bool = False
    spinner: ICustomSpinner = None

    def __init__(self):
        super().__init__()
        self.logger = CompositeLogger()
        self._dependencyResolver = DependencyResolver()
        self._dependencyResolver.put("spinner", Descriptor("templateengine-v2", "spinner", "*", "*", "1.0"))

    def configure(self, config: ConfigParams):
        self._dependencyResolver.configure(config)
        self.logger.configure(config)

    def set_references(self, references: IReferences) -> None:
        self._dependencyResolver.set_references(references)
        self._dependencyResolver.put("spinner", Descriptor("templateengine-v2", "spinner", "*", "*", "1.0"))
        self.logger.set_references(references)    
        self.spinner = self._dependencyResolver.get_one_required("spinner")

    def set_params(self, params: InputParams):
        self.params = params
        self.verbose = self.params is not None and self.params.verbose

    def set_goals(self, goals: list[IGoal]):
        self.goals = goals

    def set_tools(self, tools: dict):
        self.tools = tools

    def set_model(self, ai_model: IModel):
        self.ai_model = ai_model

    def set_metadata(self, metadata: dict) -> None:
        self.metadata = metadata

    def set(self, params: InputParams, goals: list[IGoal], tools: dict, ai_model: IModel, metadata: dict) -> None:
        self.params = params
        self.goals = goals
        self.tools = tools
        self.ai_model = ai_model
        self.metadata = metadata
        self.verbose = self.params is not None and self.params.verbose
