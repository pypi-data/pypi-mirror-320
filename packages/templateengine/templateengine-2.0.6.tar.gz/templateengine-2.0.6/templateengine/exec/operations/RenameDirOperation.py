import os
import shutil
import time

from .CommonOperation import CommonOperation

class RenameDirOperation(CommonOperation):
    def __init__(self, retries: int = 2, delay: int = 5) -> None:
        super().__init__()
        self.retries = retries
        self.delay = delay

    def run(self, operation_params) -> None:
        source = operation_params.get('source')
        destination = operation_params.get('destination')

        if not os.path.exists(source):
            e = FileNotFoundError(f"Source folder '{source}' does not exist.")
            if self.verbose:
                self.logger.fatal(None, e, f"Source folder '{source}' does not exist.")
            self.error_handling.log_exec_error(f"RenameDirOperation: Source folder '{source}' does not exist.", e)
            return

        for attempt in range(self.retries + 1):
            try:
                shutil.move(source, destination)
                if self.verbose:
                    self.logger.info(None, f"Renamed directory from '{source}' to '{destination}'")
                return  # Exit on success
            except (PermissionError, OSError) as e:
                if attempt < self.retries:
                    if self.verbose:
                        self.logger.warn(None, f"Attempt {attempt + 1} failed. Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    if self.verbose:
                        self.logger.error(None, e, f"Failed to rename directory from '{source}' to '{destination}' after {self.retries + 1} attempts.")
                    self.error_handling.log_exec_error(f"RenameDirOperation: Failed to rename directory from '{source}' to '{destination}'.", e)
                    return
