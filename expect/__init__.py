import logging
import re
import sys
from typing import Callable, Union, Any, Type, AnyStr

import oktest  # type: ignore

__all__ = ('expect', 'NOT', 'NG', 'not_ok', 'run', 'spec', 'test_that', 'fail',
           'skip', 'todo', 'options_of', 'at_end', 'subject', 'situation', 'main', 'warn')

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


ST_WARNING = "warning"


class VerboseReporter(oktest.VerboseReporter):
    INDICATOR = {**oktest.BaseReporter.INDICATOR, **{ST_WARNING: "Warning"}} 
    _counts2str_table = [*oktest.BaseReporter._counts2str_table, *[(ST_WARNING, "warning", True)]]

    def clear_counts(self):
        self.counts = {key: 0 for (key, *_) in self._counts2str_table}
    
    def exit_testcase(self, testcase, testname, status, exc_info):
        s = ""
        if status in {oktest.ST_SKIPPED, ST_WARNING, oktest.ST_TODO}:
            ex = exc_info[1]
            #reason = getattr(ex, 'reason', '')
            reason = ex.args[0]
            s = " (reason: %s)" % (reason, )
            if status != ST_WARNING:
                exc_info = ()
            else:
                if ex.exc_info:
                    exc_info = ex.exc_info

        self._super.exit_testcase(self, testcase, testname, status, exc_info)
        self._erase_temporary_str()
        indicator = self.indicator(status)
        desc = self.get_testcase_desc(testcase, testname)
        self.write("  " * self.depth + "- [%s] %s%s\n" % (indicator, desc, s))
        self.out.flush()

oktest.REPORTER = VerboseReporter

class TestRunner(oktest.TEST_RUNNER):
    instance: "TestRunner | None"
    def __init__(self, *args_, **kwargs_):
        super().__init__(*args_, **kwargs_)
        TestRunner.instance = self 

    def _run_testcase(self, testcase, testname):
        try:
            meth = getattr(testcase, testname)
            meth()
        except KeyboardInterrupt:
            raise
        except AssertionError:
            return oktest.ST_FAILED, sys.exc_info()
        except oktest.SkipTest:
            return oktest.ST_SKIPPED, sys.exc_info()
        except _Warning:
            return ST_WARNING, sys.exc_info()
        except _Todo:   # when failed expectedly
            return oktest.ST_TODO, sys.exc_info()
        except oktest._UnexpectedSuccess: # when passed unexpectedly
            #return ST_UNEXPECTED, ()
            ex = sys.exc_info()[1]
            if not ex.args:
                ex.args = ("test should be failed (because not implemented yet), but passed unexpectedly.",)
            return oktest.ST_FAILED, sys.exc_info()
        except Exception:
            return oktest.ST_ERROR, sys.exc_info()
        else:
            specs = getattr(testcase, '_oktest_specs', None)
            arr = specs and [ spec for spec in specs if spec._exception ]
            if arr: 
                return oktest.ST_FAILED, arr
            return oktest.ST_PASSED, ()


def execute(*targets, **kwargs) -> tuple[int, dict[str, int]]:
    """ Return more information about a test execution  
        The default run method returns the number of failed and errored tests only
        With this implementation we are also returning the counts dictionary so additional
        checks can be performed
    """
    try:
        TestRunner.instance = None
        oldRunner = oktest.TEST_RUNNER
        oktest.TEST_RUNNER = TestRunner
        if targets == tuple():
            # WE do the discovery otherwise run method can't find them due to frame difference
            targets = (oktest.config.TARGET_PATTERN, )
            targets = list(oktest._target_classes(targets))
            
        result = oktest.run(*targets, **kwargs)
        counts = TestRunner.instance.reporter.counts if TestRunner.instance else {}
        counts["total"] = sum(counts.values())
        return result, counts
    finally:
        oktest.TEST_RUNNER = oldRunner


oktestRun = oktest.run
def run(*targets, summary:dict[str, int] | None = None, **kwargs) -> int:
    try:
        TestRunner.instance = None
        oldRunner = oktest.TEST_RUNNER
        oktest.TEST_RUNNER = TestRunner
        if targets == tuple():
            # WE do the discovery otherwise run method can't find them due to frame difference
            targets = (oktest.config.TARGET_PATTERN, )
            targets = list(oktest._target_classes(targets))
            
        result = oktestRun(*targets, **kwargs)
        if summary is not None:
            counts = TestRunner.instance.reporter.counts if TestRunner.instance else {}
            counts["total"] = sum(counts.values())
            for key, value in counts.items():
                summary[key] = summary.get(key, 0) + value 

        return result
    
    finally:
        oktest.TEST_RUNNER = oldRunner


oktest.run = run 


class _Warning(Exception):
    def __init__(self, message: str, exc_info):
        super().__init__(message)
        self.exc_info = exc_info

class WarningObject(object):

    def __call__(self, reason: str):
        """ Stop the test execution and mark it as warning, it works similar to fail() function"""
        raise _Warning(message=reason, exc_info=[])

    def always(self, reason: str = ""):
        return self.when(True, reason)
    
    def when(self, condition: bool | Callable[[], bool], reason: str = ""):
        
        def deco(func):
            def fn(*args, __condition__=condition, **kwargs):
                try:
                    func(*args, **kwargs)
                except AssertionError as error:
                    condition = __condition__() if callable(__condition__) else __condition__
                    if condition:
                        raise _Warning(reason, sys.exc_info())
                    else:
                        raise error 
            fn.__name__ = func.__name__
            fn.__doc__  = func.__doc__
            fn._firstlineno = getattr(func, '_firstlineno', oktest.util._func_firstlineno(func))
            return fn
        return deco


warn = WarningObject()



# Support callable conditions for skip functions. This also fixes an issue with _firstlineno setting
# The issue is visible if skip comes after todo item. It was keeping the line number of todo decorator
# instead of the original function
class SkipObject(object):
    def __call__(self, reason: str):
        raise oktest.SkipTest(reason)

    def always(self, reason: str):
        return self.when(True, reason)
    
    def when(self, condition: bool | Callable[[], bool], reason: str):
        
        def deco(func):
            def fn(*args, __condition__=condition, **kwargs):
                condition = __condition__() if callable(__condition__) else __condition__
                if condition:
                    raise oktest.SkipTest(reason)
                else:
                    func(*args, **kwargs)
                 
            fn.__name__ = func.__name__
            fn.__doc__  = func.__doc__
            fn._firstlineno = getattr(func, '_firstlineno', oktest.util._func_firstlineno(func))
            return fn
        
        return deco


skip = SkipObject()

class _Todo(Exception):
    def __init__(self, message: str, exc_info):
        super().__init__(message)
        self.exc_info = exc_info

class TodoObject(object):

    def __call__(self, fn=None, reason=None):
        """ Stop the test execution and mark it as warning, it works similar to fail() function"""
        if isinstance(fn, str) and reason is None:
            reason, fn = fn, reason 
        if reason is None:
            reason = ""

        wrapper = self.when(True, reason)
        if fn is not None:
            wrapper = wrapper(fn) 
        return wrapper

    def when(self, condition: bool | Callable[[], bool], reason: str = ""):
        
        def deco(func):
            def fn(*args, __condition__=condition, **kwargs):
                condition = __condition__() if callable(__condition__) else __condition__
                if condition:
                    try:
                        func(*args, **kwargs)
                        raise oktest._UnexpectedSuccess("test should be failed (because not implemented yet), but passed unexpectedly.")
                    except AssertionError:
                        raise _Todo(reason, sys.exc_info())
                else:
                    func(*args, **kwargs)
                
            fn.__name__ = func.__name__
            fn.__doc__  = func.__doc__
            fn._firstlineno = getattr(func, '_firstlineno', oktest.util._func_firstlineno(func))
            return fn
        return deco

todo = TodoObject()


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


# testThat forces a certain test description, more towards action and validation while test is too generic
test_that = oktest.test


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
