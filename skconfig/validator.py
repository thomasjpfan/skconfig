from .parameter.base import Param
from .exceptions import InvalidParamName
from .exceptions import InactiveConditionedValue
from .exceptions import SKConfigValueError


class BaseValidator:
    conditions = []
    forbiddens = []
    estimator = None

    def __init__(self):
        # check parameters forbidden and conditions are compalible
        self.parameters_ = {
            name: param
            for name, param in self.__class__.__dict__.items()
            if isinstance(param, Param)
        }
        if self.estimator is None:
            raise SKConfigValueError("estimator must be defined")

    def validate_params(self, **kwargs):
        # Check kwargs get in params
        for name in kwargs:
            if name not in self.parameters_:
                raise InvalidParamName(name)

        all_kwargs = {**self.estimator().get_params(), **kwargs}

        # check for forbidden
        for forbidden in self.forbiddens:
            forbidden.is_forbidden(**all_kwargs)

        condition_names = [cond.child for cond in self.conditions]
        for name, value in all_kwargs.items():
            if name not in condition_names:
                self.parameters_[name].validate(name, value)

        # Check conditions
        for condition in self.conditions:
            name = condition.child
            value = all_kwargs.get(name)
            if condition.is_active(**all_kwargs):
                self.parameters_[name].validate(name, value)
            elif value is not None:
                raise InactiveConditionedValue(name, condition)

    def validate_estimator(self, estimator):
        self.validate_params(**estimator.get_params())
