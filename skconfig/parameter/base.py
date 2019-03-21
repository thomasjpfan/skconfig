from abc import ABCMeta, abstractmethod
from ..exceptions import InvalidParamType


class Param(metaclass=ABCMeta):
    @abstractmethod
    def validate(self, param):
        ...

    def __or__(self, other):
        parameters = []
        if isinstance(self, UnionParam):
            parameters.extend(self.parameters)
        else:
            parameters.append(self)
        if isinstance(other, UnionParam):
            parameters.extend(other.parameters)
        else:
            parameters.append(other)
        return UnionParam(*parameters)


class UnionParam(Param):
    def __init__(self, *parameters):
        if not isinstance(parameters, tuple) or not parameters:
            raise ValueError("parameters must be a non empty")
        for parameter in parameters:
            if not isinstance(parameter, Param):
                raise ValueError("parameters must be all Param")
        self.parameters = parameters

    def validate(self, name, value):
        for param in self.parameters:
            if isinstance(value, param.value_type):
                param.validate(name, value)
                break
        else:
            p_types = [param.value_type.__name__ for param in self.parameters]
            raise InvalidParamType(name, p_types)
