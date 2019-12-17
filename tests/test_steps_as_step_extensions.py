import pytest
import steps
from safetydance import script
from steps_as_step_extensions import initialize_test_value, validate_test_value


@script
def test_steps_as_step_extensions():
    initialize_test_value("foobar")
    validate_test_value("foobar")
    with pytest.raises(AssertionError):
        validate_test_value("This should raise AssertionError!")
