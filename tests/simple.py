from safetydance import step_data
from safetydance_test.step_extension import step_extension


simple_value = step_data(int)
simple_result = step_data(int)


@step_extension
def value_is(desired_value: int):
    simple_value = desired_value


@step_extension
def result_is(expected_result: int):
    assert simple_result == expected_result


@step_extension
def value_plus(other_value: int):
    simple_result = simple_value + other_value
