from abc import ABC, abstractmethod
from .ExecError import ExecError

class IErrorHandling(ABC):
    @abstractmethod
    def log_exec_error(self, message: str, error: Exception) -> None:
        pass

    @abstractmethod
    def get_exec_errors(self) -> list[ExecError]:
        pass

    @abstractmethod
    def clear_exec_errors(self) -> None:
        pass