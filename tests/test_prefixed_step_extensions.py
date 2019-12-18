import pytest
import example_prefix
from safetydance_test import Given, When, Then, And, scripted_test


@scripted_test
def test_steps_as_step_extensions():
    with pytest.raises(AttributeError):
        Given.initialize_test_value("foobar")
    Given.example_prefix.initialize_test_value("foobar")
    Then.example_prefix.validate_test_value("foobar")
    with pytest.raises(AssertionError):
        And.example_prefix.validate_test_value("This should raise AssertionError!")
