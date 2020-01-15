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
from types import FunctionType
from type_extensions import (
    extension,
    Extension,
    get_calling_frame,
    get_calling_frame_as_import,
    monkeypatch_extended_type,
)

def steal_context_from_calling_frame():
    calling_frame = get_calling_frame(not_calling_frame=[__name__])
    if "context" not in calling_frame.f_locals:
        raise Exception("Couldn't find context in calling frame! Are you sure you "
                "called from a script or step?")
    return calling_frame.f_locals["context"]


def call_step(f, *args, **kwargs):
    context = steal_context_from_calling_frame()
    f(context, *args, **kwargs)


class StepExtension(Extension):
    def __init__(
            self,
            f: FunctionType,
            f_resolved: FunctionType = None,
            target_type=TestStepPrefix):
        super().__init__(f, f_resolved)
        self.f_step = step(f)
        self.target_type = target_type


    def __call__(self, extended_self, *args, **kwargs):
        __tracebackhide__ = True
        call_step(self.f_step, *args, **kwargs)


    @property
    def extended_type(self):
        return self.target_type


    def __str__(self):
        return f"StepExtension  f: {self.f}"


@step_decorator
def step_extension(f, target_type: type = TestStepPrefix):
    """
    Transform a function into a type extension.
    What we want is a function f: [[TestStepPrefix, Context, *args, **kwargs], None]
    where f implicitly steals the Context from the calling scope
    """
    #FIXME figure out how to properly handle class vs instance attrs...
    calling_frame = get_calling_frame_as_import()
    if calling_frame is None:
        # If called from a notebook, looks like a getattr!
        calling_frame = get_calling_frame(not_calling_frame=[__name__])
    calling_module = calling_frame.f_globals["__name__"]
    if not hasattr(target_type, "__scoped_setattr__"):
        monkeypatch_extended_type(target_type)
    f_extension = StepExtension(f, target_type=target_type)
    target_type.__scoped_setattr__(calling_module, f.__name__, f_extension)
    return f_extension


def as_step_extension(step_to_wrap: Step, target_type: type = TestStepPrefix):
    """
    Wrap a step as a step_extension for use in testing.
    """
    return step_extension(step_to_wrap.f_original, target_type)


def all_steps_as_step_extensions_from(
        source_module,
        target_type: type = TestStepPrefix):
    """
    Wrap all steps in the ``source_module`` and add them to the calling module.
    """
    newmembers = dict()
    for k, v in getmembers(
            source_module,
            lambda x: isinstance(x, Step) and not isinstance(x, StepExtension)):
        newmembers[k] = as_step_extension(v, target_type)
    calling_frame = get_calling_frame(not_calling_frame=[__name__])
    calling_module = calling_frame.f_globals["__name__"]
    target_module = import_module(calling_module)
    all_members = []
    for k, v in newmembers.items():
        setattr(target_module, k, v)
        all_members.append(k)
    return all_members
