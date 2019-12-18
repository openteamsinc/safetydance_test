import pytest
import steps_as_step_extensions
from safetydance_test import Given, When, Then, And, scripted_test


@scripted_test
def test_steps_as_step_extensions():
    Given.initialize_test_value("foobar")
    Then.validate_test_value("foobar")
    with pytest.raises(AssertionError):
        And.validate_test_value("This should raise AssertionError!")
