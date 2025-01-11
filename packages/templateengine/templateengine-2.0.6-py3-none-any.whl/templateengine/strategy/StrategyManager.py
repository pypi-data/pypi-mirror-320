import sys
import time
from pip_services4_observability.log import CompositeLogger
from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.refer import IReferenceable, IReferences, DependencyResolver, Descriptor

from ..data.InputParams import InputParams
from ..strategy.IStrategy import IStrategy
from ..strategy.Goal import Goal
from ..cmd.CommandLineInput import CommandLineInput
from ..data.InputParams import InputParams
from ..plan.IPlanner import IPlanner
from ..ai.IModel import IModel
from .StrategyAction import StrategyAction
from ..data.errors.IErrorHandling import IErrorHandling

class StrategyManager(IConfigurable, IReferenceable):
    _dependencyResolver: DependencyResolver = None
    params: InputParams = None
    logger: CompositeLogger = None
    verbose: bool = False
    strategies_list: list[IStrategy] = []
    error_handling: IErrorHandling = None

    def __init__(self):
        self._dependencyResolver = DependencyResolver()
        self.logger = CompositeLogger()
        self._dependencyResolver.put("strategies",
                                     Descriptor("templateengine-v2",
                                                "strategy",
                                                "*", "*", "1.0"))
        self._dependencyResolver.put("planner", Descriptor("templateengine-v2", "planner", "*", "strategy-manager", "1.0"))
        self._dependencyResolver.put("ai-model", Descriptor("templateengine-v2", "ai-model", "*", "*", "1.0"))
        self._dependencyResolver.put("error-handling", Descriptor("templateengine-v2", "error-handling", "*", "*", "1.0"))
        self.params = CommandLineInput.parse(sys.argv[1:])
        self.verbose = self.params is not None and self.params.verbose

    def configure(self, config: ConfigParams):
        self._dependencyResolver.configure(config)
        self.logger.configure(config)

    def set_references(self, references: IReferences) -> None:
        self._dependencyResolver.set_references(references)
        self.logger.set_references(references)
        try: 
            self.ai_model: IModel = self._dependencyResolver.get_one_required("ai-model")
            self.planner: IPlanner = self._dependencyResolver.get_one_required("planner")
            self.strategies_list = self._dependencyResolver.get_required("strategies")
            self.error_handling = self._dependencyResolver.get_one_required("error-handling")
        except Exception as e:
            self.logger.fatal(None, e, f"Strategy manager set_references error: {e}")
            raise e
        self.ai_model.set_params(self.params)

    def run(self) -> None:
        if self.verbose:
            self.logger.info(None, f"Run strategy manager")
        start_time = time.time()

        if self.params.command is not None and len(self.params.command) > 0:
            strategy = next(filter(lambda x: x.get_name() == self.params.command, self.strategies_list))
            if self.verbose:
                self.logger.info(None, f"Selected '{strategy.get_name()}' strategy")
            strategy.set_params(self.params)
            strategy.set_metadata({})
            strategy.run()
        else:
            if self.params.specs["description"] is not None and len(self.params.specs["description"]) > 0:
                strategies_dict = self.__get_strategies_dict()
                self.planner.set(self.params, [], strategies_dict, self.ai_model, {})
                if self.verbose:
                    self.logger.info(None, f"Run strategy manager planner")
                actions: list[StrategyAction] = self.planner.run()
                if self.verbose:
                    self.logger.info(None, f"Strategy manager planner running is completed. Planned {len(actions)} strategies to run.")
                for act in actions:
                    strategy: IStrategy = next(filter(lambda x: x.get_name() == act["strategy_name"], self.strategies_list))
                    if self.verbose:
                        self.logger.info(None, f"Selected '{strategy.get_name()}' strategy")
                    strategy.set_params(self.params)
                    strategy.set_metadata(act["metadata"])
                    if self.verbose:
                        self.logger.info(None, f"Run '{strategy.get_name()}' strategy")
                    strategy.run()
            else:
                e = ValueError("Description is missing to run application")
                self.logger.fatal(None, e, f"Description is missing to run application")
                raise e
        
        end_time = time.time()
        execution_time = end_time - start_time
        if self.verbose:
            self.logger.info(None, f"Execution time: {execution_time:.2f} seconds")
        exec_errors = self.error_handling.get_exec_errors()
        if len(exec_errors) > 0:
            self.logger.info(None, f"Execution is finished with errors:")
            for err in exec_errors:
                self.logger.fatal(None, err.error, err.message)
            sys.exit(1)
        sys.exit(0)

    def __get_strategies_dict(self) -> dict:
        result = {}
        for s in self.strategies_list:
            goals = "".join([goal.get_goal() for goal in s.goals])
            result.update({s.get_name(): goals})
        return result    