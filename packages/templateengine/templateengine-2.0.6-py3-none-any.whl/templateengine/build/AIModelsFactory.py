from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor
from ..ai.OpenAIModel import OpenAIModel

class AIModelsFactory(Factory):
    __OpenAIGentDescriptor = Descriptor('templateengine-v2', 'ai-model', '*', 'openai', '1.0')

    def __init__(self):
        super().__init__()

        self.register_as_type(self.__OpenAIGentDescriptor, OpenAIModel)