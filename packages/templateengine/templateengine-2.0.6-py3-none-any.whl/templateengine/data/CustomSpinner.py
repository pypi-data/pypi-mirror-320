from yaspin import yaspin
from .ICustomSpinner import ICustomSpinner

class CustomSpinner(ICustomSpinner):
    spinner = None
    
    def __init__(self):
        self.spinner = yaspin()

    def start(self) -> None:
        self.spinner.start()

    def stop(self) -> None:
        self.spinner.stop()

    def write(self, text: str) -> None:
        self.spinner.write(text)

    def reset_spinner(self, text: str = "Processing...") -> None:
        self.spinner.text = text
        self.spinner.color = "white"

    def set_success_spinner(self, text: str) -> None:
        self.spinner.color = "green"
        self.spinner.text = text
        self.spinner.ok("✔")

    def set_failure_spinner(self, text: str, e: Exception) -> None:
        self.spinner.color = "red"
        self.spinner.text = f"{text}. Error: {e}"
        self.spinner.fail("✖")   