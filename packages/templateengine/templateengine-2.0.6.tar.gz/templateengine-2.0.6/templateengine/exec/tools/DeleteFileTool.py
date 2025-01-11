from .CommonTool import CommonTool
from ..operations.DeleteFileOperation import DeleteFileOperation
from .ToolTypes import ToolTypes
from ...data.InputParams import InputParams

class DeleteFileTool(CommonTool):
    def __init__(self) -> None:
        super().__init__()
        self.operations = [DeleteFileOperation()]
        self.params: InputParams = None

    def set_params(self, params: InputParams) -> None:
        self.params = params
        self.verbose = self.params is not None and self.params.verbose
        for op in self.operations:
            op.set_params(params)

    def get_promt(self) -> str:
        return "This tool deletes a file. Should contain path in tool_params."
    
    def get_name(self) -> str:
        return ToolTypes.DELETE_FILE    

    def validate(self, tool_params) -> None:
        path = tool_params.get('path')
        if not path:
            e = ValueError("'path' must be specified for deleting a file.")
            if self.verbose:
                if not path:
                    self.logger.fatal(None, e, f"Validation failed for {ToolTypes.DELETE_FILE} tool. 'path' must be specified for deleting a file.")            
            raise e

    def run(self, tool_params) -> None:
        if self.verbose:
            self.logger.info(None, f"Start {ToolTypes.DELETE_FILE} operations execution")        
        for op in self.operations:
            op.run(tool_params)
