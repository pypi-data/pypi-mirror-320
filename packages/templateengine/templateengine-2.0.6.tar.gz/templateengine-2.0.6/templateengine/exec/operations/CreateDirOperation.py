import os
import time
from .CommonOperation import CommonOperation

class CreateDirOperation(CommonOperation):
    def __init__(self, retries: int = 2, delay: int = 5) -> None:
        super().__init__()
        self.retries = retries
        self.delay = delay

    def run(self, operation_params) -> None:
        path = operation_params.get('path')

        for attempt in range(self.retries + 1):
            try:
                os.makedirs(path, exist_ok=True)
                if self.verbose:
                    self.logger.info(None, f"Created directory: {path}")
                return
            except (PermissionError, OSError) as e:
                if attempt < self.retries:
                    if self.verbose:
                        self.logger.warn(None, f"Attempt {attempt + 1} to create directory failed. Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    if self.verbose:
                        self.logger.error(None, e, f"Failed to create directory '{path}' after {self.retries + 1} attempts.")
                    self.error_handling.log_exec_error(f"CreateDirOperation: Failed to create dir '{path}'.", e)
                    return
