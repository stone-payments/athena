import pyArango.validation as val
from pyArango.theExceptions import ValidationError


class StringValidator(val.Validator):
    def validate(self, value):
        if not isinstance(value, str) or None:
            raise ValidationError("Field value must be a string")
        return True


class IntValidator(val.Validator):
    def validate(self, value):
        if not isinstance(value, int) or None:
            raise ValidationError("Field value must be an int")
        return True


class BoolValidator(val.Validator):
    def validate(self, value):
        if not isinstance(value, bool) or None:
            raise ValidationError("Field value must be an int")
        return True
