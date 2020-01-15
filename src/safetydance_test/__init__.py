# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound


from importlib import import_module
from safetydance import script, step_data, step_decorator, Step, NestingContext


class TestStepPrefix:
    ...


Given = step_data(TestStepPrefix)
When = step_data(TestStepPrefix)
Then = step_data(TestStepPrefix)
And = step_data(TestStepPrefix)


class ScriptedTest(Step):
    def __call__(self, *args, **kwargs):
        __tracebackhide = True
        if self.f is None:
            self.rewrite()
        context = NestingContext()
        calling_module = import_module(self.f.__module__)
        effective_TestStepPrefix = \
                getattr(calling_module, 'TestStepPrefix', None) or TestStepPrefix
        test_step_prefix = effective_TestStepPrefix()
        context[Given] = test_step_prefix
        context[When] = test_step_prefix
        context[Then] = test_step_prefix
        context[And] = test_step_prefix
        if "context" in kwargs:
            context.parent = kwargs["context"]
        kwargs["context"] = context
        self.f(*args, **kwargs)


@step_decorator
def scripted_test(f):
    return script(f, script_class=ScriptedTest)
