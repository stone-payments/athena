def not_null(value):
    if value is None:
        raise ValueError("Field value cannot be None")
    return value


def string_validate(value, not_none=False):
    if not_none:
        not_null(value)
    if not isinstance(value, str) and value is not None:
        raise ValueError("Field value must be a string")
    return value


def int_validate(value, not_none=False):
    if not_none:
        not_null(value)
    if not isinstance(value, int) and value is not None:
        raise ValueError("Field value must be an int")
    return value


def bool_validate(value, not_none=False):
    if not_none:
        not_null(value)
    if not isinstance(value, bool) and value is not None:
        raise ValueError("Field value must be an bool")
    return value
