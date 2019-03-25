from .condition import (EqualsCondition, NotEqualsCondition, LessThanCondition,
                        GreaterThanCondition, InCondition, AndCondition,
                        OrCondition)
from .forbidden import (ForbiddenEquals, ForbiddenIn, ForbiddenAnd)

from ConfigSpace import EqualsCondition as CSEqualsCondition
from ConfigSpace import NotEqualsCondition as CSNotEqualsCondition
from ConfigSpace import LessThanCondition as CSLessThanCondition
from ConfigSpace import GreaterThanCondition as CSGreaterThanCondition
from ConfigSpace import InCondition as CSInCondition
from ConfigSpace import AndConjunction as CSAndCondition
from ConfigSpace import OrConjunction as CSOrCondition
from ConfigSpace import ForbiddenAndConjunction as CSForbiddenAnd
from ConfigSpace import ForbiddenEqualsClause as CSForbiddenEqual
from ConfigSpace import ForbiddenInClause as CSForbiddenIn


def skconfig_obj_to_config_space(skconfig_obj, cs):
    if isinstance(skconfig_obj, EqualsCondition):
        child_hp = cs.get_hyperparameter(skconfig_obj.child)
        parent_hp = cs.get_hyperparameter(skconfig_obj.parent)
        return CSEqualsCondition(child_hp, parent_hp,
                                 skconfig_obj.conditioned_value)
    elif isinstance(skconfig_obj, NotEqualsCondition):
        child_hp = cs.get_hyperparameter(skconfig_obj.child)
        parent_hp = cs.get_hyperparameter(skconfig_obj.parent)
        return CSNotEqualsCondition(child_hp, parent_hp,
                                    skconfig_obj.conditioned_value)
    elif isinstance(skconfig_obj, LessThanCondition):
        child_hp = cs.get_hyperparameter(skconfig_obj.child)
        parent_hp = cs.get_hyperparameter(skconfig_obj.parent)
        return CSLessThanCondition(child_hp, parent_hp,
                                   skconfig_obj.conditioned_value)
    elif isinstance(skconfig_obj, GreaterThanCondition):
        child_hp = cs.get_hyperparameter(skconfig_obj.child)
        parent_hp = cs.get_hyperparameter(skconfig_obj.parent)
        return CSGreaterThanCondition(child_hp, parent_hp,
                                      skconfig_obj.conditioned_value)
    elif isinstance(skconfig_obj, InCondition):
        child_hp = cs.get_hyperparameter(skconfig_obj.child)
        parent_hp = cs.get_hyperparameter(skconfig_obj.parent)
        return CSInCondition(child_hp, parent_hp,
                             skconfig_obj.conditioned_value)
    elif isinstance(skconfig_obj, AndCondition):
        output = []
        for cond in skconfig_obj.conditons:
            output.append(skconfig_obj_to_config_space(cond, cs))
        return CSAndCondition(*output)
    elif isinstance(skconfig_obj, OrCondition):
        output = []
        for cond in skconfig_obj.conditons:
            output.append(skconfig_obj_to_config_space(cond, cs))
        return CSOrCondition(*output)
    elif isinstance(skconfig_obj, ForbiddenEquals):
        hp = cs.get_hyperparameter(skconfig_obj.name)
        return CSForbiddenEqual(hp, skconfig_obj.value)
    elif isinstance(skconfig_obj, ForbiddenIn):
        hp = cs.get_hyperparameter(skconfig_obj.name)
        return CSForbiddenIn(hp, skconfig_obj.value)
    elif isinstance(skconfig_obj, ForbiddenAnd):
        output = []
        for forb in skconfig_obj.forbidden_clauses:
            output.append(skconfig_obj_to_config_space(forb, cs))
        return CSForbiddenAnd(*output)
    raise TypeError("Unable to recognize type: {}".format(skconfig_obj))
