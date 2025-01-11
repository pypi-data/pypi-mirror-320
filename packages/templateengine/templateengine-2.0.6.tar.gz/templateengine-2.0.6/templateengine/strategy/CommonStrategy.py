from abc import abstractmethod
import sys
import time
from pip_services4_observability.log import CompositeLogger
from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.refer import IReferenceable, IReferences, DependencyResolver, Descriptor

from ..data.InputParams import InputParams
from ..strategy.IStrategy import IStrategy
from ..exec.Action import Action

class CommonStrategy(IStrategy, IConfigurable, IReferenceable):
    _dependencyResolver: DependencyResolver = None
    params: InputParams = None
    logger: CompositeLogger = None
    verbose: bool = False

    def __init__(self):
        super().__init__()
        self._dependencyResolver = DependencyResolver()
        self.logger = CompositeLogger()
        self._dependencyResolver.put("executor", Descriptor("templateengine-v2", "executor", "*", "*", "1.0"))
        self._dependencyResolver.put("ai-model", Descriptor("templateengine-v2", "ai-model", "*", "*", "1.0"))
        self.tools = []
        # define goals
        self.set_goals()

    def configure(self, config: ConfigParams):
        self._dependencyResolver.configure(config)
        self.logger.configure(config)

    def set_references(self, references: IReferences) -> None:
        self._dependencyResolver.set_references(references)
        self.logger.set_references(references)
        try: 
            self.executor = self._dependencyResolver.get_one_required("executor")
            self.ai_model = self._dependencyResolver.get_one_required("ai-model")
            self.planner = self._dependencyResolver.get_one_required("planner")
        except Exception as e:
            self.logger.fatal(None, e, f"Common strategy set_references error: {e}")
            raise e

    def set_params(self, params: InputParams):
        self.params = params
        self.verbose = self.params is not None and self.params.verbose
        self.ai_model.set_params(self.params)

    def set_metadata(self, metadata: dict) -> None:
        self.metadata = metadata

    def run(self) -> None:
        # Planning block        
        ops_dict = self.__get_ops_dict()
        self.planner.set(self.params, self.goals, ops_dict, self.ai_model, self.metadata)
        if self.verbose:
            self.logger.info(None, f"Run planner")
        actions: list[Action] = self.planner.run()

        # Execution block
        if self.verbose:
            self.logger.info(None, f"Run executor validation")
        self.executor.validate(self.params, actions)
        if self.verbose:
            self.logger.info(None, f"Run executor operations")        
        self.executor.run(self.params, actions)

    def __get_ops_dict(self) -> dict:
        result = {}
        for op in self.tools:
            prompt = self.executor.get_tool_promt(op)
            result.update({op: prompt})
        return result