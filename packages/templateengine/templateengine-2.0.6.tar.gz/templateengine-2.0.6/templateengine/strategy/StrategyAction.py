from typing import Any

class StrategyAction():
    strategy_name: str = None
    metadata: dict = None

    def __init__(self, strategy_name: str, metadata):
        self.strategy_name = strategy_name
        self.metadata = metadata

    def get_name(self) -> str:
        return self.strategy_name
    
    def get_metadata(self) -> Any:
        return self.metadata    
    
    @staticmethod
    def get_prompt() -> str:
        prompt = (
            "The result should be a json object StrategyAction -> {\n"
            "\"strategy_name\": \"strategy name from the list of available strategies\",\n"
            "\"metadata\": \"strategy parameters for its execution based on the description, input params and the project structure\"\n"
            "}"
        )
        return prompt