from .ExecError import ExecError
from .IErrorHandling import IErrorHandling

class ErrorHandling(IErrorHandling):    
    def __init__(self):
        self._exec_errors = []

    def log_exec_error(self, message: str, error: Exception) -> None:
        self._exec_errors.append(ExecError(message=message, error=error))

    def get_exec_errors(self) -> list[ExecError]:
        return self._exec_errors

    def clear_exec_errors(self) -> None:
        self._exec_errors.clear()