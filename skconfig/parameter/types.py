from .base import Param
from ..exceptions import InvalidParamType
from ..exceptions import InvalidParamChoices


class BoolParam(Param):
    value_type = bool

    def validate(self, name, value):
        if not isinstance(value, self.value_type):
            raise InvalidParamType(name, self.value_type.__name__)


class NoneParam(Param):
    value_type = type(None)

    def validate(self, name, value):
        if not isinstance(value, self.value_type):
            raise InvalidParamType(name, self.value_type.__name__)


class FloatParam(Param):
    value_type = (float, int)

    def validate(self, name, value):
        if not isinstance(value, self.value_type):
            name = ",".join(v.__name__ for v in self.value_type)
            raise InvalidParamType(name, self.value_type.__name__)


class IntParam(Param):
    value_type = int

    def validate(self, name, value):
        if not isinstance(value, self.value_type):
            raise InvalidParamType(name, self.value_type.__name__)


class StringParam(Param):
    value_type = str

    def __init__(self, *choices):
        if not isinstance(choices, tuple) or not choices:
            raise ValueError("choices must be a non empty")
        for choice in choices:
            if not isinstance(choice, self.value_type):
                raise ValueError("choices must be all strings")
        self.choices = choices

    def validate(self, name, value):
        if not isinstance(value, self.value_type):
            raise InvalidParamType(name, self.value_type.__name__)
        if value not in self.choices:
            raise InvalidParamChoices(name, self.choices)
