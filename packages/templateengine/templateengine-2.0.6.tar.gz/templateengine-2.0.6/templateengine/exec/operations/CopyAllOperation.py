import shutil
import os
import time
from .CommonOperation import CommonOperation

class CopyAllOperation(CommonOperation):
    def __init__(self, retries: int = 2, delay: int = 5) -> None:
        super().__init__()
        self.retries = retries
        self.delay = delay

    def run(self, operation_params) -> None:
        source = operation_params.get('source')
        destination = operation_params.get('destination')
        ignore_list = operation_params.get('ignore_list', [])

        for attempt in range(self.retries + 1):
            try:
                if not os.path.exists(source):
                    e = FileNotFoundError(f"Source folder '{source}' does not exist.")
                    if self.verbose:
                        self.logger.fatal(None, e, f"Source folder '{source}' does not exist.")
                    raise e

                # Ensure the destination folder exists
                os.makedirs(destination, exist_ok=True)

                # Copy the entire directory tree
                for item in os.listdir(source):
                    if item in ignore_list:
                        continue

                    src_item = os.path.join(source, item)
                    dest_item = os.path.join(destination, item)

                    if os.path.isdir(src_item):
                        shutil.copytree(src_item, dest_item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_item, dest_item)
                
                if self.verbose:
                    self.logger.info(None, f"Copied all from folder '{source}' to '{destination}'")
                return  # Exit on success
            except (PermissionError, OSError) as e:
                if attempt < self.retries:
                    if self.verbose:
                        self.logger.warn(None, f"Attempt {attempt + 1} to copy all contents failed. Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    if self.verbose:
                        self.logger.error(None, e, f"Failed to copy all contents from '{source}' to '{destination}' after {self.retries + 1} attempts.")
                    self.error_handling.log_exec_error(f"CopyAllOperation: Failed to copy all from '{source}' to '{destination}'.", e)
                    return
