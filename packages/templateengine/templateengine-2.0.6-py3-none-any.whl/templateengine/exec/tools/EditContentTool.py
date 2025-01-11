from .CommonTool import CommonTool
from ..operations.EditContentOperation import EditContentOperation
from .ToolTypes import ToolTypes
from ...data.InputParams import InputParams

class EditContentTool(CommonTool):
    def __init__(self) -> None:
        super().__init__()
        self.operations = [EditContentOperation()]
        self.params: InputParams = None

    def set_params(self, params: InputParams) -> None:
        self.params = params
        self.verbose = self.params is not None and self.params.verbose
        for op in self.operations:
            op.set_params(params)

    def get_promt(self) -> str:
        return "This tool edits the content of a file. Should contain path(full path) and old_path(full path before replacements) in tool_params."
    
    def get_name(self) -> str:
        return ToolTypes.EDIT_CONTENT    

    def validate(self, tool_params) -> None:        
        path = tool_params.get('path')
        content = tool_params.get('content', '') or ''
        
        if not path:
            e = ValueError("'path' must be specified for editing content.")
            if self.verbose:
                self.logger.fatal(None, e, f"Validation failed for {ToolTypes.EDIT_CONTENT} tool. 'path' must be specified for editing content.")
            raise e
        if content is None:
            e = ValueError("'content' must be specified for editing content.")
            if self.verbose:
                self.logger.fatal(None, e, f"Validation failed for {ToolTypes.EDIT_CONTENT} tool. 'content' must be specified for editing content for path: {path}.")
            raise e
        if self.verbose:
            self.logger.info(None, f"Validation completed successfully for {ToolTypes.EDIT_CONTENT} tool. Content and path: {path} are correct")

    def run(self, tool_params) -> None:
        if self.verbose:
            self.logger.info(None, f"Start {ToolTypes.EDIT_CONTENT} operations execution")
        for op in self.operations:
            op.run(tool_params)
