class InvalidParam(ValueError):
    pass


class InvalidParamName(InvalidParam):
    def __init__(self, name):
        super().__init__("{} is a invalid parameter name".format(name))


class InvalidParamType(InvalidParam):
    def __init__(self, name, correct_type):
        super().__init__("{} must be of type {}".format(name, correct_type))


class InvalidParamRange(InvalidParam):
    def __init__(self,
                 name,
                 value,
                 lower=None,
                 upper=None,
                 include_lower=True,
                 include_upper=True):
        if lower is None and upper is None:
            raise ValueError("Lower and uppoer bounds cannot both be None")

        msg_list = ["{} with value {} not in range:".format(name, value)]
        if lower is not None:
            if include_lower:
                lower_str = "[{},".format(lower)
            else:
                lower_str = "({},".format(lower)
            msg_list.append(lower_str)
        else:
            msg_list.append("(-inf")

        if upper is not None:
            if include_upper:
                upper_str = "{}]".format(upper)
            else:
                upper_str = "{})".format(upper)
            msg_list.append(upper_str)
        else:
            msg_list.append("inf)")
        super().__init__(" ".join(msg_list))


class InvalidParamChoices(InvalidParam):
    def __init__(self, name, choices):
        super().__init__("{} must be one of {}".format(name, choices))


class ForbiddenValue(ValueError):
    def __init__(self, name, value):
        super().__init__("{} with value {} is forbidden".format(name, value))


class InactiveConditionedValue(ValueError):
    def __init__(self, name, condition):
        super().__init__("{} has an unmet condition: {}".format(
            name, condition))
