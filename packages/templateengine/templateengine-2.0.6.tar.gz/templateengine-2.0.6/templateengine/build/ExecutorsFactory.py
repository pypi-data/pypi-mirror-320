from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor
from ..exec.Executor import Executor

class ExecutorsFactory(Factory):
    __ExecutorDescriptor = Descriptor('templateengine-v2', 'executor', '*', '*', '1.0')

    def __init__(self):
        super().__init__()

        self.register_as_type(self.__ExecutorDescriptor, Executor)    