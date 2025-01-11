from abc import ABC, abstractmethod
from .ISession import ISession
from ..data.InputParams import InputParams

class IModel(ABC): 
    @abstractmethod
    def create_session(self, session_id: str) -> ISession:        
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> ISession:
        pass

    @abstractmethod
    def get_sessions_list(self) -> list[ISession]:        
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        pass

    @abstractmethod
    def delete_sessions(self) -> None:
        pass

    @abstractmethod
    def set_params(self, params: InputParams) -> None:
        pass