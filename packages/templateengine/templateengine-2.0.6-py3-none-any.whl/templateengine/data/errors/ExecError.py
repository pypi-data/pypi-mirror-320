from datetime import datetime

class ExecError:
    def __init__(self, message: str, error: Exception):
        self._timestamp = datetime.now().isoformat()
        self._message = message
        self._error = error

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @property
    def error(self) -> Exception:
        return self._error

    @error.setter
    def error(self, value: Exception) -> None:
        self._error = value