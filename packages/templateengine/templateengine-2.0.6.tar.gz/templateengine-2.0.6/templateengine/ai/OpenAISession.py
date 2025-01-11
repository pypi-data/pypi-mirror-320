import uuid
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from .ISession import ISession
from .IPromptBuilder import IPromptBuilder

class OpenAISession(ISession): 
    def __init__(self, client, model: str, session_id: str = None):
        self.client: OpenAI = client
        self.model = model
        self.temperature = 1
        self.messages = []
        self.chat: ChatCompletion = None
        self.session_id = session_id if session_id is not None else str(uuid.uuid4())

    def get_id(self) -> str:
        return self.session_id

    def send_prompt(self, cleanup_response = True) -> str:
        self.build()
        self.chat = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=self.messages)
        assistant_response = self.chat.choices[0].message.content.strip()
        self.messages.append({"role": "assistant", "content": assistant_response})
        if cleanup_response:
            return self.remove_first_and_last_line(assistant_response)
        return assistant_response
    
    def build(self):
        pass

    def reset_roles(self) -> IPromptBuilder:
        self.messages.clear()
        return self

    def add_role(self, role: str, content: str) -> IPromptBuilder:
        self.messages.append({"role": role, "content": content})
        return self


    def update_role_content(self, role: str, content: str) -> IPromptBuilder:
        index = next((i for i, item in enumerate(self.messages) if item["role"] == role), -1)
        self.messages[index]["content"] = content
        return self


    def add_default_system_role(self) -> IPromptBuilder:
        self.messages.append({"role": "system", "content": "You are a helpful assistant."})
        return self

    def set_temperature(self, temperature: float) -> IPromptBuilder:
        self.temperature = temperature
        return self
    
    def remove_first_and_last_line(self, text: str):
        first_line = text.split('\n')[0]
        if first_line.startswith('```'):
            lines = text.splitlines()
            if len(lines) > 2:  # Ensure there are at least 3 lines to remove first and last
                lines = lines[1:-1]
            return "\n".join(lines)
        else:
            return text     