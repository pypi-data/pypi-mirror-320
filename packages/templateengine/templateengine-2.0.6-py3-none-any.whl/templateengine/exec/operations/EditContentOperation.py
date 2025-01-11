import os
import time
from .CommonOperation import CommonOperation

class EditContentOperation(CommonOperation):
    def __init__(self, retries: int = 2, delay: int = 5) -> None:
        super().__init__()
        self.retries = retries
        self.delay = delay

    def run(self, operation_params) -> None:
        path = operation_params.get('path')
        content = operation_params.get('content', '') or ""

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        for attempt in range(self.retries + 1):
            try:
                if not os.path.isfile(path):
                    e = FileNotFoundError(f"Source file '{path}' does not exist.")
                    if self.verbose:
                        self.logger.fatal(None, e, f"Source file '{path}' does not exist.")
                    self.error_handling.log_exec_error(f"EditContentOperation: Source file '{path}' does not exist.", e)
                    return

                with open(path, 'w') as f:
                    f.write(content)
                if self.verbose:
                    self.logger.info(None, f"Edited content of file '{path}'")
                return  # Exit on success
            except (PermissionError, OSError) as e:
                if attempt < self.retries:
                    if self.verbose:
                        self.logger.warn(None, f"Attempt {attempt + 1} to edit file failed. Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    if self.verbose:
                        self.logger.error(None, e, f"Failed to edit content of file '{path}' after {self.retries + 1} attempts.")
                    self.error_handling.log_exec_error(f"EditContentOperation: Failed to edit content of file '{path}'.", e)
                    return
