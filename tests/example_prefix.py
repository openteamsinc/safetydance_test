from safetydance_test import TestStepPrefix
from safetydance_test.step_extension import all_steps_as_step_extensions_from, step_extension
import steps as steps
from type_extensions import extension_property


class ExamplePrefix():
    """
    This class is a placeholder for type_extension functions to hang off of.
    """
    ...


@extension_property
def example_prefix(self: TestStepPrefix):
    ret = ExamplePrefix()
    print(dir(ret))
    return ret


all_steps_as_step_extensions_from(steps, target_type=ExamplePrefix)
