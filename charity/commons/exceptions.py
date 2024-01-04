from django.core.exceptions import ValidationError

class NullArgumentError(ValidationError):
    pass