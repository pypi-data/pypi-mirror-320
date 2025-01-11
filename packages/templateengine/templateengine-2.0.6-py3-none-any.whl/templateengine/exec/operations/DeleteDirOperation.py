import os
import shutil
import time
from .CommonOperation import CommonOperation

class DeleteDirOperation(CommonOperation):
    def __init__(self, retries: int = 2, delay: int = 5) -> None:
        super().__init__()
        self.retries = retries
        self.delay = delay

    def run(self, operation_params) -> None:
        path = operation_params.get('path')

        for attempt in range(self.retries + 1):
            try:
                if not os.path.exists(path):
                    e = FileNotFoundError(f"Directory '{path}' does not exist.")
                    if self.verbose:
                        self.logger.fatal(None, e, f"Directory '{path}' does not exist.")
                    raise e

                shutil.rmtree(path)
                if self.verbose:
                    self.logger.info(None, f"Deleted directory: {path}")
                return
            except (PermissionError, OSError) as e:
                if attempt < self.retries:
                    if self.verbose:
                        self.logger.warn(None, f"Attempt {attempt + 1} to delete directory failed. Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    if self.verbose:
                        self.logger.error(None, e, f"Failed to delete directory '{path}' after {self.retries + 1} attempts.")
                    self.error_handling.log_exec_error(f"DeleteDirOperation: Failed to delete dir '{path}'.", e)
                    return
