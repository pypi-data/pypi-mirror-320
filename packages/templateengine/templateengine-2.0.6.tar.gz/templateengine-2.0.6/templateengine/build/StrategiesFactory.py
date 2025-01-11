from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor
from ..strategy import CreateComponentSkeletonStrategy, ParseDescriptionStrategy

class StrategiesFactory(Factory):
    __CreateComponentSkeletonStrategyDescriptor = Descriptor('templateengine-v2', 'strategy', '*', 'create-skeleton', '1.0')
    __ParseDescriptionStrategyDescriptor = Descriptor('templateengine-v2', 'strategy', '*', 'parse-description', '1.0')

    def __init__(self):
        super().__init__()

        self.register_as_type(self.__CreateComponentSkeletonStrategyDescriptor, CreateComponentSkeletonStrategy)
        self.register_as_type(self.__ParseDescriptionStrategyDescriptor, ParseDescriptionStrategy)