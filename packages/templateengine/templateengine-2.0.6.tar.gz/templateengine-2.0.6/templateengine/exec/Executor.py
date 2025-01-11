from pip_services4_components.refer import IReferenceable, DependencyResolver, IReferences, Descriptor
from pip_services4_observability.log import CompositeLogger
from pip_services4_components.config import IConfigurable, ConfigParams
from yaspin import yaspin
from ..data.InputParams import InputParams
from .tools.ITool import ITool
from .IExecutor import IExecutor
from .Action import Action
from ..data.ICustomSpinner import ICustomSpinner

class Executor(IExecutor, IConfigurable, IReferenceable):
    _dependencyResolver = None
    _tools: ITool = None
    _ops_map = {}
    logger: CompositeLogger = None
    verbose: bool = False
    spinner: ICustomSpinner = None

    def __init__(self):
        self._dependencyResolver = DependencyResolver()
        self.logger = CompositeLogger()
        self._dependencyResolver.put("tools", Descriptor("templateengine-v2", "tool", "*", "*", "1.0"))
        self._dependencyResolver.put("spinner", Descriptor("templateengine-v2", "spinner", "*", "*", "1.0"))

    def configure(self, config: ConfigParams):
        self._dependencyResolver.configure(config)
        self.logger.configure(config)

    def set_references(self, references: IReferences) -> None:
        self._dependencyResolver.set_references(references)
        self.logger.set_references(references)            
        try: 
            self._tools = self._dependencyResolver.get_required("tools")
            self.spinner = self._dependencyResolver.get_one_required("spinner")
            op: ITool
            for op in self._tools:
                self._ops_map.update({op.get_name(): op.get_promt()})
        except Exception as e:
            self.logger.fatal(None, e, f"Executor set_references error: {e}")
            raise e

    def get_tool_promt(self, tool_name: str) -> str:
        return self._ops_map.get(tool_name)        

    def validate(self, params: InputParams, actions: list[Action]):
        self.spinner.reset_spinner()
        self.verbose = params is not None and params.verbose
        try:
            self.spinner.start()
            if self.verbose:
                self.logger.info(None, "Validation is starting")
            for act in actions:
                tool = next(filter(lambda x: x.get_name() == act["tool_name"], self._tools))
                tool.set_params(params)
                tool.validate(act["tool_params"])            
            self.spinner.set_success_spinner("Validation completed successfully!")
        except Exception as e:
            self.spinner.set_failure_spinner("Error in Executor.validate() is occurred.", e)
            raise e
        finally:
            self.spinner.stop()

    def run(self, params: InputParams, actions: list[Action]):
        self.spinner.reset_spinner()
        self.verbose = params is not None and params.verbose
        try:
            self.spinner.start()
            if self.verbose:
                self.logger.info(None, "Tools execution is starting")
            for act in actions:
                tool = next(filter(lambda x: x.get_name() == act["tool_name"], self._tools))
                tool.set_params(params)
                tool.run(act["tool_params"])
            self.spinner.set_success_spinner("Tools execution completed successfully!")            
        except Exception as e:
            self.spinner.set_failure_spinner("Error in Executor.run() is occurred.", e)
            raise e
        finally:
            self.spinner.stop()