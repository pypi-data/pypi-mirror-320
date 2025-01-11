from typing import Any

class Action():
    tool_name = None
    tool_params = None

    def __init__(self, tool_name: str, tool_params):
        self.tool_name = tool_name
        self.tool_params = tool_params

    def get_name(self) -> str:
        return self.tool_name
    
    def get_params(self) -> Any:
        return self.tool_params    
    
    @staticmethod
    def get_prompt() -> str:
        prompt = (
            "The result should be a json object Action -> {\n"
            "\"tool_name\": \"tool name from the list of available tools\",\n"
            "\"tool_params\": \"tool parameters for its execution based on the description of the tools above and the project structure\"\n"
            "}"
        )
        return prompt