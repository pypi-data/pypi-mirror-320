from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.refer import IReferenceable, IReferences, DependencyResolver, Descriptor
from pip_services4_observability.log import CompositeLogger
from .ITool import ITool
from ...data.errors.IErrorHandling import IErrorHandling
from ..operations.IOperation import IOperation

class CommonTool(ITool, IConfigurable, IReferenceable):
    logger: CompositeLogger = None
    verbose: bool = False
    _dependencyResolver: DependencyResolver = None
    error_handling: IErrorHandling = None
    operations = []

    def __init__(self) -> None:
        self.logger = CompositeLogger()
        self._dependencyResolver = DependencyResolver()
        self._dependencyResolver.put("error-handling", Descriptor("templateengine-v2", "error-handling", "*", "*", "1.0"))

    def configure(self, config: ConfigParams):
        self.logger.configure(config)
        self._dependencyResolver.configure(config)
        for op in self.operations:
            op.configure(config)

    def set_references(self, references: IReferences):
        self.logger.set_references(references)
        self._dependencyResolver.set_references(references)
        self.error_handling = self._dependencyResolver.get_one_required("error-handling")
        for op in self.operations:
            op.set_references(references)
    