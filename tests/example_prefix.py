from safetydance_test import TestStepPrefix
from safetydance_test.step_extension import all_steps_as_step_extensions_from, step_extension
from type_extensions import extension_property
import steps


class ExamplePrefix():
    """
    This class is a placeholder for type_extension functions to hang off of.
    """
    ...


_EXAMPLE = ExamplePrefix()


@extension_property
def example_prefix(self: TestStepPrefix):
    return _EXAMPLE


all_steps_as_step_extensions_from(steps, target_type=ExamplePrefix)
