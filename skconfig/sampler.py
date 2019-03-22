from contextlib import suppress

import ConfigSpace as CS
from .distribution import load_dist_dict
from .exceptions import SKConfigValueError
from .distribution import BaseDistribution
from .condition import AndCondition
from .condition import OrCondition
from .forbidden import ForbiddenAnd
from .forbidden import ForbiddenEquals
from .forbidden import ForbiddenIn


class Sampler:
    def __init__(self, validator, **kwargs):
        self.hps = {}
        for k, v in kwargs.items():
            if k in validator.parameters_:
                if not isinstance(v, BaseDistribution):
                    self.hps[k] = v
                else:
                    raise SKConfigValueError("{} is not a distribution",
                                             format(k))
            else:
                raise SKConfigValueError("{} is an invalid key".format(k))
        self.validator = validator
        self._generate_config_space()

    def to_dict(self):
        output = {}
        for k, v in self.hps.items():
            output[k] = v.to_dict()
        return output

    def from_dict(self, p_dict):
        for k, v in p_dict.items():
            self.hps[k] = load_dist_dict(v)
        self._generate_config_space()

    def _generate_config_space(self):
        active_params = set(self.hps)
        active_conditions = []
        activate_forbiddens = []

        # Find activate conditions
        for cond in self.validator.conditions:
            if cond.child not in active_params:
                continue

            active_cond = self._get_active_condition(cond)
            if active_cond is None:
                with suppress(KeyError):
                    active_params.remove(cond.child)
                continue
            active_conditions.append(active_cond)

        # Find activate forbiddens
        for forb in self.validator.forbiddens:
            if forb.name not in active_params:
                continue
            active_forb = self._get_active_forbidden(forb)
            if active_forb is None:
                continue
            activate_forbiddens.append(active_forb)

        # Create configuration space
        cs = CS.ConfigurationSpace()
        for name in active_params:
            self.hps[name].add_to_config_space(name, cs)

        for cond in active_conditions:
            pass

        self.config_space = cs

    def sample(self, size=1):
        configs = self.config_space.sample_configuration(size)
        if size == 1:
            configs = [configs]
        output = []
        for config in configs:
            config_dict = config.get_dictionary()
            for name, dist in self.hps.items():
                dist.post_process(name, config_dict)
            output.append(config_dict)
        return output

    def _get_active_condition(self, cond):
        if isinstance(cond, OrCondition):
            output = []
            for inner_cond in cond.conditions:
                active_cond = self._active_condition(inner_cond)
                if active_cond is None:
                    continue
                output.append(active_cond)
            if not output:
                return None
            return OrCondition(*output)
        if isinstance(cond, AndCondition):
            for inner_cond in cond.conditions:
                active_cond = self._active_condition(inner_cond)
                if active_cond is None:
                    return None
            return cond

        parent = cond.parent
        if parent not in self.hps:
            return None
        conditioned_value = cond.conditioned_value
        dist = self.hps[parent]
        if dist.in_distrubution(conditioned_value):
            return cond

    def _get_active_forbidden(self, forbidden):
        if isinstance(forbidden, ForbiddenAnd):
            for forb in forbidden.forbidden_clauses:
                name = forb.name
                dist = self.hps[name]
                if not dist.in_distrubution(forb.value):
                    return None
            return forbidden
        elif isinstance(forbidden, ForbiddenIn):
            values = []
            name = forbidden.name
            dist = self.hps[name]
            for value in forbidden.value:
                if dist.in_distrubution(forbidden.value):
                    values.append(value)
            if not values:
                return None
            return ForbiddenIn(name, values)
        elif isinstance(forbidden, ForbiddenEquals):
            # ForbiddenEquals
            name = forbidden.name
            dist = self.hps[name]
            if dist.in_distrubution(forbidden.value):
                return forbidden
            return None
        raise TypeError("Unrecognized type {}".format(forbidden))

    def _generate_cs_condition(self, cond):
        pass
