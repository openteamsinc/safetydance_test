from ast import (
    arg,
    fix_missing_locations,
    Load,
    Name,
)
from importlib import import_module
from inspect import getmembers
from safetydance import step, step_decorator, Step
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
    Transform a function into a type extension.
    What we want is a function f: [[TestStepPrefix, Context, *arg, **kwarg], None]
    where f implicitly steals the Context from the calling scope
    """
    #FIXME figure out how to properly handle class vs instance attrs...
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


def as_step_extension(step_to_wrap: Step):
    """
    Wrap a step as a step_extension for use in testing.
    """
    return step_extension(step_to_wrap.f_original)


def all_steps_as_step_extensions_from(source_module):
    """
    Wrap all steps in the ``source_module`` and add them to the calling module.
    """
    newmembers = dict()
    for k, v in getmembers(
            source_module,
            lambda x: isinstance(x, Step) and not isinstance(x, StepExtension)):
        newmembers[k] = as_step_extension(v)
    calling_frame = get_calling_frame(not_calling_frame=[__name__])
    calling_module = calling_frame.f_globals["__name__"]
    target_module = import_module(calling_module)
    all_members = []
    for k, v in newmembers.items():
        setattr(target_module, k, v)
        all_members.append(k)
    return all_members
