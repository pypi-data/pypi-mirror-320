import os
import shutil
import time
from .CommonOperation import CommonOperation

class CopyFileOperation(CommonOperation):
    def __init__(self, retries: int = 2, delay: int = 5) -> None:
        super().__init__()
        self.retries = retries
        self.delay = delay

    def run(self, operation_params) -> None:
        source = operation_params.get('source')
        destination = operation_params.get('destination')

        for attempt in range(self.retries + 1):
            try:
                if not os.path.isfile(source):
                    e = FileNotFoundError(f"Source file '{source}' does not exist.")
                    if self.verbose:
                        self.logger.fatal(None, e, f"Source file '{source}' does not exist.")
                    raise e

                shutil.copy2(source, destination)
                if self.verbose:
                    self.logger.info(None, f"Copied file from '{source}' to '{destination}'")
                return
            except (PermissionError, OSError) as e:
                if attempt < self.retries:
                    if self.verbose:
                        self.logger.warn(None, f"Attempt {attempt + 1} to copy file failed. Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    if self.verbose:
                        self.logger.error(None, e, f"Failed to copy file from '{source}' to '{destination}' after {self.retries + 1} attempts.")
                    self.error_handling.log_exec_error(f"CopyFileOperation: Failed to copy file from '{source}' to '{destination}'.", e)
                    return
