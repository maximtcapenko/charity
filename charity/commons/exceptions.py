from django.core.exceptions import ValidationError


class NullArgumentError(ValidationError):
    pass


class ApplicationError(Exception):
    def __init__(self, message, return_url, code=None, params=None):
        super().__init__(message, code, params)

        self.return_url = return_url
        self.error_message = message
