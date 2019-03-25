from .base import Param
from ..exceptions import InvalidParamRange
from ..exceptions import InvalidParamType


class NumericalInterval(Param):
    def __init__(self,
                 lower=None,
                 upper=None,
                 include_lower=True,
                 include_upper=True):
        self.lower = lower
        self.upper = upper
        self.include_lower = include_lower
        self.include_upper = include_upper

    def validate(self, name, value):
        if not isinstance(value, self.value_type):
            raise InvalidParamType(name, self.type_str)

        if self.lower is not None:
            if self.include_lower:
                lower_in_range = self.lower <= value
            else:
                lower_in_range = self.lower < value
            if not lower_in_range:
                raise InvalidParamRange(
                    name,
                    value,
                    lower=self.lower,
                    upper=self.upper,
                    include_lower=self.include_lower,
                    include_upper=self.include_upper)

        if self.upper is not None:
            if self.include_upper:
                upper_in_range = value <= self.upper
            else:
                upper_in_range = value < self.upper
            if not upper_in_range:
                raise InvalidParamRange(
                    name,
                    value,
                    lower=self.lower,
                    upper=self.upper,
                    include_lower=self.include_lower,
                    include_upper=self.include_upper)


class FloatIntervalParam(NumericalInterval):
    value_type = (float, int)
    type_str = 'float, int'


class IntIntervalParam(NumericalInterval):
    value_type = int
    type_str = 'int'
