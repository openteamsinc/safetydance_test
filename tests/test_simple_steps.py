from safetydance_test import Given, When, Then, And, scripted_test
import simple


@scripted_test
def test_simple_sum():
    Given.value_is(42)
    When.value_plus(1)
    Then.result_is(43)
