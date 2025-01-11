from abc import ABC, abstractmethod
from ...data.InputParams import InputParams

class IOperation(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def set_params(self, params: InputParams) -> None:
        pass
        
    @abstractmethod
    def run(self, operation_params) -> None:
        pass