import logging
from typing import Callable, Union

import oktest  # type: ignore

__all__ = ('expect', 'NOT', 'NG', 'not_ok', 'run', 'spec', 'test_that', 'fail',
           'skip', 'todo', 'options_of', 'at_end', 'subject', 'situation', 'main')

#
# Re-use from oktest
#

NOT = oktest.NOT
NG = oktest.NG
not_ok = oktest.not_ok 
run = oktest.run 
spec = oktest.spec
fail = oktest.fail
options_of = oktest.options_of
at_end = oktest.at_end
subject = oktest.subject
situation = oktest.situation
# TODO: More investigation needed to use main from oktest. I got recursion errors when I called this method
# main = oktest.main

#
# Customizations
#

# I simply like better to read it "expect(True) != False" rather than "ok(True) != False"
expect = oktest.ok


# Support callable conditions for skip functions
class SkipWithRuntimeConditionEvaluation(object):
    def __call__(self, reason: str):
        raise oktest.SkipTest(reason)

    def when(self, condition: Union[bool, Callable], reason):
        if callable(condition):
            condition_ = condition
        else:
            def condition_():
                return condition

        def deco(func):
            def fn(self):
                if condition_():
                    raise oktest.SkipTest(reason)
                else:
                    func(self)
            fn.__name__ = func.__name__
            fn.__doc__ = func.__doc__
            fn._firstlineno = oktest.util._func_firstlineno(func)
            return fn
        return deco

    def unless(self, condition: Union[bool, Callable], reason: str):
        if callable(condition):
            condition_ = condition
        else:
            def condition_():
                return condition

        def deco(func):
            def fn(self):
                if not condition_():
                    raise oktest.SkipTest(reason)
                else:
                    func(self)
            fn.__name__ = func.__name__
            fn.__doc__ = func.__doc__
            fn._firstlineno = oktest.util._func_firstlineno(func)
            return fn

        return deco


skip = SkipWithRuntimeConditionEvaluation()


# testThat forces a certain test description, more towards action and validation while test is too generic
test_that = oktest.test


# This is to ensure that todo tests are shown without altering the order, oktest shows them at the end
def todo(func: Callable):
    deco = oktest.todo(func) 
    deco._firstlineno = func.__code__.co_firstlineno
    return deco 


#
# Test Execution
#
def main():
    oktest.mainapp.MainApp.main()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
