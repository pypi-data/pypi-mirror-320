import os
import sys
from openai import OpenAI

from ..exec.Action import Action
from .IModel import IModel
from .ISession import ISession
from .OpenAISession import OpenAISession
from ..data.InputParams import InputParams

class OpenAIModel(IModel):
    def __init__(self):
        self.sessions: list[OpenAISession] = []

    def create_session(self, session_id: str) -> ISession:
        session = OpenAISession(client=self.client, model=self.model_name, session_id=session_id)
        self.sessions.append(session)
        return session
        
    def get_session(self, session_id: str) -> ISession:
        return next(filter(lambda x: x.get_id() == session_id, self.sessions), None)

    def get_sessions_list(self) -> list[ISession]:        
        return self.sessions

    def delete_session(self, session_id: str) -> None:
        index = next((i for i, item in enumerate(self.sessions) if item.get_id() == session_id), -1)
        if index >= 0:
            self.sessions[index].chat = None
            self.sessions.pop(index)
        else:
            print(f"Session with id={session_id} is not defined")

    def delete_sessions(self) -> None:
        for session in self.sessions:
            session.chat = None
        self.sessions.clear()

    def set_params(self, params: InputParams):
        self.params = params
        self.verbose = self.params is not None and self.params.verbose
        api_key = params.api_key
        if not api_key:
            raise ValueError("OpenAI API key must be provided or set in environment variables.")
        try:
            # Initialize the OpenAI client
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            raise ConnectionError("Failed to initialize OpenAI client. Check API key and network connectivity.") from e
        self.model_name = params.model