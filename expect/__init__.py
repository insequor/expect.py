import logging
import re
from typing import Callable, Union, Any, Type, AnyStr

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
@oktest.assertion
def is_subclass_of(self, arg):
    boolean = issubclass(self.target, arg)
    if boolean == self.boolean: return self
    self.failed(f"{self.target} is not subclass of {arg}")
    

@oktest.assertion
def is_not_subclass_of(self, arg):
    boolean = not issubclass(self.target, arg)
    if boolean == self.boolean: return self
    self.failed(f"{self.target} is subclass of {arg}")
    


# oktest adds the assertions at runtime, but that means we do not get type hints
# 
class AssertionObject(oktest.AssertionObject):
    
    def __eq__(self, other: Any):
        super().__eq__(other)

    def __ne__(self, other: Any):
        super().__ne__(other)

    def __gt__(self, other: Any):
        super().__gt__(other)

    def __ge__(self, other: Any):
        super().__ge__(other)

    def __lt__(self, other: Any):
        super().__lt__(other)

    def __le__(self, other: Any):
        super().__le__(other)

    def between(self, min: Any, max: Any) -> "AssertionObject":
        return super().between(min, max)

    def in_delta(self, other: Any, delta: Any) -> "AssertionObject":
        return super().in_delta(other, delta)

    def in_(self, other: set[Any] | list[Any] | dict[Any, Any]):
        super().in_(other)

    def not_in(self, other: set[Any] | list[Any] | dict[Any, Any]):
        super().not_in(other)

    def contains(self, other: Any):
        super().contains(other)

    def not_contain(self, other: Any):
        super().not_contain(other)

    def is_(self, other: Any):
        super().is_(other)

    def is_not(self, other: Any):
        super().is_not(other)

    def is_a(self, other: type):
        super().is_a(other)

    def is_not_a(self, other: type):
        super().is_not_a(other)

    def is_subclass_of(self, arg):
        super().is_subclass_of(arg)
        
    def is_not_subclass_of(self, arg):
        super().is_not_subclass_of(arg)
        

    def has_attr(self, name: str):
        super().has_attr(name)

    # Hidden in favor of using in_
    # def has_key(self, key: Any) -> "AssertionObject":
    #    return super().has_key(key)  # type: ignore

    def has_item(self, key: Any, val: Any) -> "AssertionObject":
        return super().has_item(key, val)

    def attr(self, name: Any, expected: Any):
        super().attr(name, expected)

    def matches(self, pattern: AnyStr | re.Pattern, flags: int = 0):
        super().matches(pattern, flags)
        
    def not_match(self, pattern: AnyStr | re.Pattern, flag: int = 0):
        super().not_match(pattern, flag)

    def length(self, n: int):
        super().length(n)

    def is_file(self):
        super().is_file()

    def not_file(self):
        super().not_file()

    def is_dir(self):
        super().is_dir()

    def not_dir(self):
        super().not_dir()

    def exists(self):
        super().exists()

    def not_exist(self):
        super().not_exists()

    def is_truthy(self):
        super().is_truthy()

    def is_falsy(self):
        super().is_falsy()

    def all(self, func: Callable) -> "AssertionObject":
        return super().all(func)

    def any(self, func: Callable) -> "AssertionObject":
        return super().any(func)

    def raises(self, exception_class: Type[Exception], errmsg: str | None = None):
        super().raises(exception_class, errmsg)

    def not_raise(self, exception_class: Type[Exception] = Exception):
        super().not_raise(exception_class)


oktest.ASSERTION_OBJECT = AssertionObject


# I simply like better to read it "expect(True) != False" rather than "ok(True) != False
# We are providing type hints by forwarding the call rather than just assigning a variable
def expect(statement: Any) -> AssertionObject:
    return oktest.ok(statement)  # type: ignore


class RequiredAssertionObject(oktest.AssertionObject):
    def _assertion_error(self, msg, file, line, diff):
        msg = f"(FAILED PRE/POST CONDITION) {msg}"
        ex = Exception(diff and msg + "\n" + diff or msg)
        ex.file = file;  ex.line = line;  ex.diff = diff;  ex.errmsg = msg
        ex._raised_by_oktest = True
        return ex 

def require(statement: Any) -> RequiredAssertionObject:
    """require is identical to expect in its usage. However it is used for cases where we want to 
       validate a pre or post condition for our action, rather than the expectation that we want 
       to test. For example, if your expectation is related to the content of a file you might require 
       that the file is there. 
       Unlike expect, require will raise an Exception rather than AssertionError. This will cause the test 
       to have Error status, not Fail. This is what we want, we could not properly execute our test 
       since a pre-condition failed"""
    oldObjectType = oktest.ASSERTION_OBJECT
    oktest.ASSERTION_OBJECT = RequiredAssertionObject
    assertionObject = expect(statement)
    oktest.ASSERTION_OBJECT = oldObjectType
    return assertionObject


# Support callable conditions for skip functions. This also fixes an issue with _firstlineno setting
# The issue is visible if skip comes after todo item. It was keeping the line number of todo decorator
# instead of the original function
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
            lineno = getattr(func, '_firstlineno', None) or oktest.util._func_firstlineno(func)
            fn._firstlineno = lineno
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
            lineno = getattr(func, '_firstlineno', None) or oktest.util._func_firstlineno(func)
            fn._firstlineno = lineno
            return fn

        return deco


skip = SkipWithRuntimeConditionEvaluation()


# testThat forces a certain test description, more towards action and validation while test is too generic
test_that = oktest.test


# This is to ensure that todo tests are shown without altering the order, oktest shows them at the end
def todo(func: Callable):
    deco = oktest.todo(func) 
    lineno = getattr(func, '_firstlineno', None) or oktest.util._func_firstlineno(func)
    deco._firstlineno = lineno
    return deco 


# TODO: Fail the test case if there is no test executed (no tests, or all skipped). There should be at least one
# pass or todo test.

# TODO: Print the call stack information for the exception related assertions

# TODO: Concept of failing the test case in the first error or executing all tests (workflow vs coverage ?)
 
#
# Test Execution
#
def main():
    oktest.mainapp.MainApp.main()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
