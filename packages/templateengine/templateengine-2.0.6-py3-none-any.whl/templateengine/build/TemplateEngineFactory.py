from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor
from ..TemplateEngine import TemplateEngine
from ..data.CustomSpinner import CustomSpinner
from ..data.errors.ErrorHandling import ErrorHandling

class TemplateEngineFactory(Factory):
    __TemplateEngineDescriptor = Descriptor('templateengine-v2', 'controller', '*', '*', '1.0')
    __CustomSpinnerDescriptor = Descriptor('templateengine-v2', 'spinner', '*', '*', '1.0')
    __ErrorHandlingDescriptor = Descriptor('templateengine-v2', 'error-handling', '*', '*', '1.0')

    def __init__(self):
        super().__init__()

        self.register_as_type(self.__TemplateEngineDescriptor, TemplateEngine)
        self.register_as_type(self.__CustomSpinnerDescriptor, CustomSpinner)
        self.register_as_type(self.__ErrorHandlingDescriptor, ErrorHandling)