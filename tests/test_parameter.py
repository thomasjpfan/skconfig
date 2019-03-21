from skconfig.parameter import BoolParam


def test_bool_param_type():
    p = BoolParam()
    assert p.value_type == bool
