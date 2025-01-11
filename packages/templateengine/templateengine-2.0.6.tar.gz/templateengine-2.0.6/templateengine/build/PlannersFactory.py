from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor
from ..plan import CreateComponentSkeletonPlanner, ParseDescriptionPlanner, StrategyManagerPlanner

class PlannersFactory(Factory):
    __CreateComponentSkeletonPlannerDescriptor = Descriptor('templateengine-v2', 'planner', '*', 'create-skeleton', '1.0')
    __ParseDescriptionPlannerDescriptor = Descriptor('templateengine-v2', 'planner', '*', 'parse-description', '1.0')
    __StrategyManagerPlannerDescriptor = Descriptor('templateengine-v2', 'planner', '*', 'strategy-manager', '1.0')

    def __init__(self):
        super().__init__()

        self.register_as_type(self.__CreateComponentSkeletonPlannerDescriptor, CreateComponentSkeletonPlanner)
        self.register_as_type(self.__ParseDescriptionPlannerDescriptor, ParseDescriptionPlanner)
        self.register_as_type(self.__StrategyManagerPlannerDescriptor, StrategyManagerPlanner)