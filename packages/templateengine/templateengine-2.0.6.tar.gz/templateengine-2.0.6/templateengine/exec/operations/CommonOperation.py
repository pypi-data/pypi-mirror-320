from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.refer import IReferenceable, IReferences, DependencyResolver, Descriptor
from pip_services4_observability.log import CompositeLogger
from .IOperation import IOperation
from ...data.InputParams import InputParams
from ...data.errors.IErrorHandling import IErrorHandling

class CommonOperation(IOperation, IReferenceable, IConfigurable):
    logger: CompositeLogger = None
    verbose: bool = False
    params: InputParams = None
    _dependencyResolver: DependencyResolver = None
    error_handling: IErrorHandling = None

    def __init__(self) -> None:
        self.logger = CompositeLogger()
        self._dependencyResolver = DependencyResolver()
        self._dependencyResolver.put("error-handling", Descriptor("templateengine-v2", "error-handling", "*", "*", "1.0"))

    def set_params(self, params: InputParams) -> None:
        self.params = params
        self.verbose = self.params is not None and self.params.verbose

    def configure(self, config: ConfigParams):
        self.logger.configure(config)
        self._dependencyResolver.configure(config)

    def set_references(self, references: IReferences):
        self.logger.set_references(references)
        self._dependencyResolver.set_references(references)
        self.error_handling = self._dependencyResolver.get_one_required("error-handling")        

