from abc import ABC, abstractmethod

class ICustomSpinner(ABC):  
    def __init__(self):
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def write(self, text: str) -> None:
        pass

    @abstractmethod
    def reset_spinner(self, text: str = "Processing...") -> None:
        pass

    @abstractmethod
    def set_success_spinner(self, text: str) -> None:
        pass

    @abstractmethod
    def set_failure_spinner(self, text: str, e: Exception) -> None:
        pass