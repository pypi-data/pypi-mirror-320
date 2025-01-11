from abc import ABC, abstractmethod
from .IPromptBuilder import IPromptBuilder

class ISession(IPromptBuilder): 
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def send_prompt(self, cleanup_response = True) -> str:
        pass