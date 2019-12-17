from safetydance import step, step_data


test_value = step_data(str)


@step
def initialize_test_value(value: str):
    test_value = value


@step
def validate_test_value(expected_value: str):
    assert test_value == expected_value
