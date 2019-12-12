from ast import (
    arg,
    fix_missing_locations,
    Load,
    Name,
)
from safetydance import step, step_decorator
from safetydance_test import TestStepPrefix
from type_extensions import (
    ExtendableType,
    extension,
    Extension,
    get_calling_frame,
    get_calling_frame_as_import,
    replace_with_extendable_type,
)


def steal_context_from_calling_frame():
    calling_frame = get_calling_frame(not_calling_frame=[__name__])
    if "context" not in calling_frame.f_locals:
        raise Exception("Couldn't find context in calling frame!")
    return calling_frame.f_locals["context"]


def call_step(f, *arg, **kwarg):
    context = steal_context_from_calling_frame()
    f(context, *arg, **kwarg)


class StepExtension(Extension):
    def __init__(self, f):
        self.f = f
        self.f_step = step(f)
        self.f_resolved = None


    def __call__(self, *arg, **kwarg):
        call_step(self.f_step, *arg, **kwarg)


    @property
    def extended_type(self):
        return TestStepPrefix


@step_decorator
def step_extension(f):
    """
    Transform a function into a type extension
    #FIXME figure out how to properly handle class vs instance attrs...
    What we want is a function f: TestStepPrefix -> (Context ->) *arg -> **kwarg ->
    where f implicitly steals the Context from the calling scope
    """
    target_type = TestStepPrefix
    calling_frame = get_calling_frame_as_import()
    if calling_frame is None:
        # If called from a notebook, looks like a getattr!
        calling_frame = get_calling_frame(not_calling_frame=[__name__])
    calling_module = calling_frame.f_globals["__name__"]
    if ExtendableType not in target_type.__bases__:
        target_type = replace_with_extendable_type(target_type, calling_module)
    f_extension = StepExtension(f)
    target_type.__scoped_setattr__(calling_module, f.__name__, f_extension)
    return f_extension
