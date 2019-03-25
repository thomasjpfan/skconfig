from contextlib import suppress

import ConfigSpace as CS
from .distribution import load_dist_dict
from .exceptions import SKConfigValueError
from .distribution import BaseDistribution
from .condition import AndCondition
from .condition import OrCondition
from .condition import InCondition
from .condition import EqualsCondition
from .condition import Condition
from .forbidden import ForbiddenAnd
from .forbidden import ForbiddenEquals
from .forbidden import ForbiddenIn

from .mapping import skconfig_obj_to_config_space


class Sampler:
    def __init__(self, validator, **kwargs):
        self.hps = {}
        for k, v in kwargs.items():
            if k in validator.parameters_:
                if isinstance(v, BaseDistribution):
                    self.hps[k] = v
                else:
                    raise SKConfigValueError(
                        "{} is not a distribution".format(k))
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

    def __repr__(self):
        lines = []
        for k, v in self.hps.items():
            lines.append("{}: {}".format(k, v))
        return "\n".join(lines)

    def _generate_config_space(self):
        active_params = set(self.hps)
        active_conditions = []
        active_forbiddens = []

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
            active_forb = self._get_active_forbidden(forb, active_params)
            if active_forb is None:
                continue
            active_forbiddens.append(active_forb)

        # Create configuration space
        config_space = CS.ConfigurationSpace()
        self.config_space = config_space

        for name in active_params:
            self.hps[name].add_to_config_space(name, config_space)

        self.normalized_conditions = [
            self._normalize_condition_names(cond) for cond in active_conditions
        ]

        self.normalized_forbiddens = [
            self._normalize_forbidden_names(forb) for forb in active_forbiddens
        ]

        self.cs_conditions = [
            skconfig_obj_to_config_space(cond, config_space)
            for cond in self.normalized_conditions
        ]
        self.cs_forbiddens = [
            skconfig_obj_to_config_space(forb, config_space)
            for forb in self.normalized_forbiddens
        ]
        config_space.add_conditions(self.cs_conditions)
        config_space.add_forbidden_clauses(self.cs_forbiddens)

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
                active_cond = self._get_active_condition(inner_cond)
                if active_cond is None:
                    continue
                output.append(active_cond)
            if not output:
                return None
            return OrCondition(*output)

        if isinstance(cond, AndCondition):
            for inner_cond in cond.conditions:
                active_cond = self._get_active_condition(inner_cond)
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

    def _get_active_forbidden(self, forbidden, active_params):
        if isinstance(forbidden, ForbiddenAnd):
            values = []
            for forb in forbidden.forbidden_clauses:
                name = forb.name
                if name not in active_params:
                    return
                dist = self.hps[name]
                active_forb = self._get_active_forbidden(forb, active_params)
                if active_forb is None:
                    return
                values.append(active_forb)
            return ForbiddenAnd(values)
        elif isinstance(forbidden, ForbiddenIn):
            name = forbidden.name
            if name not in active_params:
                return

            values = []
            dist = self.hps[name]
            for value in forbidden.value:
                if (dist.in_distrubution(value) and not dist.is_constant()):
                    values.append(value)
            if not values:
                return
            return ForbiddenIn(name, values)
        elif isinstance(forbidden, ForbiddenEquals):
            name = forbidden.name
            if name not in active_params:
                return

            dist = self.hps[name]
            if (dist.in_distrubution(forbidden.value)
                    and not dist.is_constant()):
                return forbidden
            return
        raise TypeError("Unrecognized type {}".format(forbidden))

    def _normalize_condition_names(self, condition):
        if isinstance(condition, (AndCondition, OrCondition)):
            output = []
            for cond in condition.conditions:
                new_conditions = self._normalize_condition_names(cond)
                output.extend(new_conditions)
            return condition.__class__(*output)
        elif isinstance(condition, InCondition):
            output = []
            for c_value in condition.conditioned_value:
                child = condition.child
                parent = condition.parent
                child_dist = self.hps[child]
                parent_dist = self.hps[parent]
                child = child_dist.child_name(child)
                parent, c_value = parent_dist.value_to_name_value(
                    parent, c_value)
                output.append(EqualsCondition(child, parent, c_value))
            return OrCondition(*output)
        elif isinstance(condition, Condition):
            child = condition.child
            parent = condition.parent
            conditioned_value = condition.conditioned_value
            child_dist = self.hps[child]
            parent_dist = self.hps[parent]

            child = child_dist.child_name(child)
            parent, conditioned_value = parent_dist.value_to_name_value(
                parent, conditioned_value)

            return condition.__class__(child, parent, conditioned_value)
        raise TypeError("Unrecognized type {}".format(condition))

    def _normalize_forbidden_names(self, forbidden):
        if isinstance(forbidden, ForbiddenAnd):
            output = []
            for forb in forbidden.forbidden_clauses:
                output.append(self._normalize_forbidden_names(forb))
            return ForbiddenAnd(output)
        elif isinstance(forbidden, ForbiddenIn):
            values = []
            dist = self.hps[forbidden.name]
            f_name = None
            for value in forbidden.value:
                name, value = dist.value_to_name_value(forbidden.name, value)
                if f_name is None:
                    f_name = name
                elif f_name != name:
                    raise ValueError("ForbiddenIn must be the same type: {}".
                                     format(forbidden))
                values.append(value)
            return ForbiddenIn(f_name, values)
        elif isinstance(forbidden, ForbiddenEquals):
            dist = self.hps[forbidden.name]
            name, value = dist.value_to_name_value(forbidden.name,
                                                   forbidden.value)
            return forbidden.__class__(name, value)
        raise TypeError("Unrecognized type {}".format(forbidden))
