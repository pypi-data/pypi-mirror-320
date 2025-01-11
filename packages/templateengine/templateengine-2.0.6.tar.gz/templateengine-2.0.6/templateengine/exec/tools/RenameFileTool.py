from .CommonTool import CommonTool
from ..operations.RenameFileOperation import RenameFileOperation
from .ToolTypes import ToolTypes
from ...data.InputParams import InputParams

class RenameFileTool(CommonTool):
    def __init__(self) -> None:
        super().__init__()
        self.operations = [RenameFileOperation()]
        self.params: InputParams = None

    def set_params(self, params: InputParams) -> None:
        self.params = params
        self.verbose = self.params is not None and self.params.verbose
        for op in self.operations:
            op.set_params(params)

    def get_promt(self) -> str:
        return "This tool renames a file. Should contain source and destination in tool_params."
    
    def get_name(self) -> str:
        return ToolTypes.RENAME_FILE    

    def validate(self, tool_params) -> None:
        source = tool_params.get('source')
        destination = tool_params.get('destination')
        if not source or not destination:
            e = ValueError("Both 'source' and 'destination' must be specified for renaming a file.")
            if self.verbose:
                if not source:
                    self.logger.fatal(None, e, f"Validation failed for {ToolTypes.RENAME_FILE} tool. 'source' must be specified for renaming a file.")
                if not destination:
                    self.logger.fatal(None, e, f"Validation failed for {ToolTypes.RENAME_FILE} tool. 'destination' must be specified for renaming a file.")            
            raise e

    def run(self, tool_params) -> None:
        if self.verbose:
            self.logger.info(None, f"Start {ToolTypes.RENAME_FILE} operations execution")        
        for op in self.operations:
            op.run(tool_params)
