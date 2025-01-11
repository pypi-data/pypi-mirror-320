import os
import time
from .CommonOperation import CommonOperation

class DeleteFileOperation(CommonOperation):
    def __init__(self, retries: int = 2, delay: int = 5) -> None:
        super().__init__()
        self.retries = retries
        self.delay = delay

    def run(self, operation_params) -> None:
        path = operation_params.get('path')

        for attempt in range(self.retries + 1):
            try:
                if not os.path.exists(path):
                    e = FileNotFoundError(f"File '{path}' does not exist.")
                    if self.verbose:
                        self.logger.fatal(None, e, f"File '{path}' does not exist.")
                    raise e

                os.remove(path)
                if self.verbose:
                    self.logger.info(None, f"Deleted file: {path}")
                return
            except (PermissionError, OSError) as e:
                if attempt < self.retries:
                    if self.verbose:
                        self.logger.warn(None, f"Attempt {attempt + 1} to delete file failed. Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    if self.verbose:
                        self.logger.error(None, e, f"Failed to delete file '{path}' after {self.retries + 1} attempts.")
                    self.error_handling.log_exec_error(f"DeleteFileOperation: Failed to delete file '{path}'.", e)
                    return
