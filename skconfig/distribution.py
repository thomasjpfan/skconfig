from abc import ABCMeta
from inspect import getfullargspec

from ConfigSpace import EqualsCondition
from ConfigSpace.hyperparameters import CategoricalHyperparameter
from ConfigSpace.hyperparameters import UniformIntegerHyperparameter
from ConfigSpace.hyperparameters import UniformFloatHyperparameter
from ConfigSpace.hyperparameters import Constant


class BaseDistribution(metaclass=ABCMeta):
    def to_dict(self):
        arg_spec = getfullargspec(self.__init__)
        args = arg_spec.args[1:]
        args.extend(arg_spec.kwonlyargs)
        output = {arg: getattr(self, arg) for arg in args}
        output['type'] = self.__class__.__name__
        return output

    @classmethod
    def from_dict(cls, p_dict):
        type_of_dict = p_dict['type']
        assert type_of_dict == cls.__name__
        return cls(**p_dict)

    def __repr__(self):
        as_dict = self.to_dict()
        type_of_dict = as_dict['type']
        del as_dict['type']
        value_str = ", ".join("{}={}".format(k, v) for k, v in as_dict.items())
        return "{}({})".format(type_of_dict, value_str)

    def post_process(self, name, config_space_dict, value=None):
        if value is not None:
            config_space_dict[name] = value
        return config_space_dict

    def value_to_name_value(self, name, value):
        return (name, value)

    def child_name(self, name):
        return name

    def is_constant(self):
        return False


class UnionDistribution(BaseDistribution):
    def __init__(self, *dists, **kwargs):
        self.dists = list(dists)

    def to_dict(self):
        output = {'type': self.__class__.__name__}
        output_dists = []
        for dist in self.dists:
            output_dists.append(dist.to_dict())
        output['dists'] = output_dists
        return output

    @classmethod
    def from_dict(cls, p_dict):
        type_of_dict = p_dict['type']
        assert type_of_dict == cls.__name__
        dists = p_dict['dists']
        dist_objs = []
        for dist in dists:
            dist_objs.append(load_dist_dict(dist))
        return cls(*dist_objs)

    def add_to_config_space(self, name, cs):
        control_name = "{}:control".format(name)

        type_name_to_dist = self.type_name_to_dist(name)
        type_names = list(type_name_to_dist)
        control = CategoricalHyperparameter(
            name=control_name, choices=type_names, default_value=type_names[0])

        cs.add_hyperparameter(control)
        for type_name, dist in type_name_to_dist.items():
            cs_hp = dist.add_to_config_space(type_name, cs)
            cs.add_condition(EqualsCondition(cs_hp, control, type_name))

    def post_process(self, name, config_space_dict):
        type_name_to_dist = self.type_name_to_dist(name)
        control_name = "{}:control".format(name)
        control_value = config_space_dict[control_name]
        dist = type_name_to_dist[control_value]

        actual_value = config_space_dict[control_value]
        dist.post_process(name, config_space_dict, value=actual_value)

        del config_space_dict[control_name]
        del config_space_dict[control_value]
        return config_space_dict

    def type_name_to_dist(self, name):
        type_name_to_dist = {}
        for dist in self.dists:
            type_name = "{}:{}".format(name, dist.dtype.__name__)
            type_name_to_dist[type_name] = dist
        return type_name_to_dist

    @property
    def type_to_dist(self):
        if hasattr(self, "_type_to_dist"):
            return self._type_to_dist
        self._type_to_dist = {}
        for dist in self.dists:
            self._type_to_dist[dist.dtype] = dist
        return self._type_to_dist

    def value_to_name_value(self, name, value):
        for dist in self.dists:
            if isinstance(value, dist.dtype):
                return "{}:{}".format(name, dist.dtype.__name__), value
        raise TypeError("Unrecognized type for name, {}, with value {}".format(
            name, value))

    def child_name(self, name):
        return "{}:control".format(name)

    def in_distrubution(self, value):
        for dist_type, dist in self.type_to_dist.items():
            if isinstance(value, dist_type):
                return dist.in_distrubution(value)
        return False


class UniformBoolDistribution(BaseDistribution):
    dtype = bool

    def __init__(self, default=True, **kwargs):
        self.default = default

    def add_to_config_space(self, name, cs):
        default_value = 'T' if self.default else 'F'
        hp = CategoricalHyperparameter(
            name=name, choices=['T', 'F'], default_value=default_value)
        cs.add_hyperparameter(hp)
        return hp

    def post_process(self, name, config_space_dict, value=None):
        value = config_space_dict[name]
        config_space_dict[name] = value == 'T'
        return config_space_dict

    def in_distrubution(self, value):
        return value in [True, False]

    def value_to_name(self, name, value):
        if value:
            return name, 'T'
        return name, 'F'


class UniformIntDistribution(BaseDistribution):
    dtype = int

    def __init__(self, lower, upper, default=None, log=False, **kwargs):
        self.lower = lower
        self.upper = upper
        self.log = log
        self.default = self.lower if default is None else default

    def add_to_config_space(self, name, cs):
        hp = UniformIntegerHyperparameter(
            name=name,
            lower=self.lower,
            upper=self.upper,
            log=self.log,
            default_value=self.default)
        cs.add_hyperparameter(hp)
        return hp

    def in_distrubution(self, value):
        return self.lower <= value <= self.upper


class UniformFloatDistribution(BaseDistribution):
    dtype = float

    def __init__(self, lower, upper, default=None, log=False, **kwargs):
        self.lower = lower
        self.upper = upper
        self.log = log
        self.default = self.lower if default is None else default

    def add_to_config_space(self, name, cs):
        hp = UniformFloatHyperparameter(
            name=name,
            lower=self.lower,
            upper=self.upper,
            log=self.log,
            default_value=self.default)
        cs.add_hyperparameter(hp)
        return hp

    def in_distrubution(self, value):
        return self.lower <= value <= self.upper


class CategoricalDistribution(BaseDistribution):
    dtype = str

    def __init__(self, choices, default=None, **kwargs):
        self.choices = choices
        self.default = self.choices[0] if default is None else default

    def add_to_config_space(self, name, cs):
        hp = CategoricalHyperparameter(
            name=name, choices=self.choices, default_value=self.default)
        cs.add_hyperparameter(hp)
        return hp

    def in_distrubution(self, value):
        return value in self.choices


class ConstantDistribution(BaseDistribution):
    def __init__(self, value, **kwargs):
        self.value = value
        self.dtype = type(value)

    def to_dict(self):
        return {'type': self.__class__.__name__, 'value': self.value}

    @classmethod
    def from_dict(cls, p_dict):
        assert p_dict['type'] == cls.__name__
        return cls(**p_dict)

    def add_to_config_space(self, name, cs):
        if self.value is None:
            hp = Constant(name, type(None).__name__)
        else:
            hp = Constant(name, self.value)
        cs.add_hyperparameter(hp)
        return hp

    def post_process(self, name, config_space_dict, value=None):
        config_space_dict[name] = self.value
        return config_space_dict

    def in_distrubution(self, value):
        return self.value == value

    def is_constant(self):
        return True


def load_dist_dict(dist_dict):
    supported_dists = [
        UniformBoolDistribution, UniformIntDistribution,
        UniformFloatDistribution, CategoricalDistribution,
        ConstantDistribution, UnionDistribution
    ]
    name_to_dist_cls = {d.__name__: d for d in supported_dists}
    dist_cls = name_to_dist_cls[dist_dict['type']]
    return dist_cls.from_dict(dist_dict)
