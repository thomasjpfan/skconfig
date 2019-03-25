from numpy.random import RandomState
from .types import NoneParam
from .types import ObjectParam
from .types import IntParam
from .types import UnionParam


def RandomStateParam():
    return UnionParam(NoneParam(), IntParam(), ObjectParam(RandomState))
