from pip_services4_components.run import IOpenable
from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.refer import IReferenceable, IReferences
from .strategy.StrategyManager import StrategyManager


class TemplateEngine(IOpenable, IConfigurable, IReferenceable):
    manager: StrategyManager = None

    def __init__(
            self
    ):
        self.manager = StrategyManager()

    def configure(self, config: ConfigParams):
        self.manager.configure(config)

    def set_references(self, references: IReferences):
        self.manager.set_references(references)

    def open(self, context):
        self.manager.run()

    def close(self, context):
        pass
