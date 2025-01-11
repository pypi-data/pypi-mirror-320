from .CommonTool import CommonTool
from ..operations.DeleteDirOperation import DeleteDirOperation
from .ToolTypes import ToolTypes
from ...data.InputParams import InputParams

class DeleteDirTool(CommonTool):
    def __init__(self) -> None:
        super().__init__()
        self.operations = [DeleteDirOperation()]
        self.params: InputParams = None

    def set_params(self, params: InputParams) -> None:
        self.params = params
        self.verbose = self.params is not None and self.params.verbose
        for op in self.operations:
            op.set_params(params)

    def get_promt(self) -> str:
        return "This tool deletes a directory. Should contain path in tool_params."
    
    def get_name(self) -> str:
        return ToolTypes.DELETE_DIR    

    def validate(self, tool_params) -> None:
        path = tool_params.get('path')
        if not path:
            e = ValueError("'path' must be specified for deleting a directory.")
            if self.verbose:
                if not path:
                    self.logger.fatal(None, e, f"Validation failed for {ToolTypes.DELETE_DIR} tool. 'path' must be specified for deleting a directory.")
            raise e

    def run(self, tool_params) -> None:
        if self.verbose:
            self.logger.info(None, f"Start {ToolTypes.DELETE_DIR} operations execution")        
        for op in self.operations:
            op.run(tool_params)
