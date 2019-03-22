from typing import Callable

from .base import Param
from ..exceptions import InvalidParamType
from ..exceptions import InvalidParamChoices
from ..exceptions import SKConfigValueError


class TypedParam(Param):
    def validate(self, name, value):
        if not isinstance(value, self.value_type):
            raise InvalidParamType(name, self.type_str)


class BoolParam(TypedParam):
    value_type = bool
    type_str = 'bool'


class NoneParam(TypedParam):
    value_type = type(None)
    type_str = 'NoneType'


class FloatParam(TypedParam):
    value_type = (float, int)
    type_str = 'float, int'


class IntParam(TypedParam):
    value_type = int
    type_str = 'int'


class StringParam(Param):
    value_type = str
    type_str = 'str'

    def __init__(self, *choices):
        if not isinstance(choices, tuple) or not choices:
            raise SKConfigValueError("choices must be all strings")
        for choice in choices:
            if not isinstance(choice, self.value_type):
                raise SKConfigValueError("choices must be all strings")
        self.choices = choices

    def validate(self, name, value):
        if not isinstance(value, self.value_type):
            raise InvalidParamType(name, self.type_str)
        if value not in self.choices:
            raise InvalidParamChoices(name, self.choices)


class CallableParam(TypedParam):
    value_type = Callable
    type_str = 'callable'


class ObjectParam(Param):
    value_type = object
    type_str = 'object'

    def __init__(self, *objects):
        self.objects = objects

    def validate(self, name, value):
        if not isinstance(value, self.objects):
            raise InvalidParamType(name, self.type_str)


class UnionParam(Param):
    def __init__(self, *parameters):
        if not isinstance(parameters, tuple) or not parameters:
            raise SKConfigValueError("parameters must be a non empty")
        for parameter in parameters:
            if not isinstance(parameter, Param):
                raise SKConfigValueError("parameters must be all Param")
        self.parameters = parameters

    def validate(self, name, value):
        for param in self.parameters:
            if isinstance(value, param.value_type):
                param.validate(name, value)
                break
        else:
            p_types = [param.type_str for param in self.parameters]
            raise InvalidParamType(name, p_types)
