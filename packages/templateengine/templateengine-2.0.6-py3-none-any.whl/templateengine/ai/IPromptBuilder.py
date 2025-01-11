from abc import ABC, abstractmethod
from typing import TypeVar, Type

# Define a generic type for the builder
T = TypeVar("T", bound="IPromptBuilder")

class IPromptBuilder(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def reset_roles(self: T) -> T:
        pass

    @abstractmethod
    def add_role(self: T, role: str, content: str) -> T:
        pass

    @abstractmethod
    def update_role_content(self: T, role: str, content: str) -> T:
        pass

    @abstractmethod
    def add_default_system_role(self: T) -> T:
        pass

    @abstractmethod
    def set_temperature(self: T, temperature: float) -> T:
        pass