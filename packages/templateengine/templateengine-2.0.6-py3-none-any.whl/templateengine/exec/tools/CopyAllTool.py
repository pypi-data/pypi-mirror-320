from .CommonTool import CommonTool
from ..operations.CopyAllOperation import CopyAllOperation
from .ToolTypes import ToolTypes
from ...data.InputParams import InputParams

class CopyAllTool(CommonTool):
    def __init__(self) -> None:
        super().__init__()
        self.operations = [CopyAllOperation()]
        self.params: InputParams = None

    def set_params(self, params: InputParams) -> None:
        self.params = params
        self.verbose = self.params is not None and self.params.verbose
        for op in self.operations:
            op.set_params(params)

    def get_promt(self) -> str:
        return "This tool copies the contents of one folder (including files and subdirectories) to another folder. Should contains source, destination and ignore_list in tool_params."
    
    def get_name(self) -> str:
        return ToolTypes.COPY_ALL

    def validate(self, tool_params) -> None:
        source = tool_params.get('source')
        destination = tool_params.get('destination')
        if not source or not destination:
            e = ValueError("Both 'source' and 'destination' must be specified for copying a directories and files.")
            if self.verbose:
                if not source:
                    self.logger.fatal(None, e, f"Validation failed for {ToolTypes.COPY_ALL} tool. 'source' must be specified for copying directories and files.")
                if not destination:
                    self.logger.fatal(None, e, f"Validation failed for {ToolTypes.COPY_ALL} tool. 'destination' must be specified for copying directories and files.")
            raise e

    def run(self, tool_params) -> None:
        if self.verbose:
            self.logger.info(None, f"Start {ToolTypes.COPY_ALL} operations execution")
        for op in self.operations:
            op.run(tool_params)
