"""
    Testing the todo decorator
"""
# Standard Import
from io import StringIO 

# Third Party Imports 

# Internal Imports
from expect import expect, todo, test_that, run, fail

class TodoTestCase:
    @test_that("Existing behavior: a test marked with todo decorator and failing is reported as todo")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            @todo 
            def _(_):
                expect(True).is_falsy()
        summary = {}
        result = run(MyTestCase, out=StringIO(), summary=summary)
        expect(result) == 0
        expect(summary["todo"]) == 1
        expect(summary["fail"]) == 0

    @test_that("Existing behavior: a test marked with todo decorator but NOT failing is reported as failure, and log says unexpected success")
    def _(_):
        class MyTestCase:
            @test_that("todo test as fail")
            @todo 
            def _(_):
                expect(True).is_truthy()
        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        expect(result) == 1
        expect(summary["todo"]) == 0
        expect(summary["fail"]) == 1
        out.seek(0)
        report = out.read()
        # print("\n\n", report)
        expect(report).contains("_UnexpectedSuccess: test should be failed (because not implemented yet), but passed unexpectedly.")

    @test_that("todo decorator can be used to with a descriptions explaining the todo reason which is printed near the test", tag="debug")
    def _(_):
        class MyTestCase:
            @test_that("todo test with description")
            @todo("just for testing")
            def _(_):
                expect(True).is_falsy()
        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        expect(result) == 0
        expect(summary["todo"]) == 1
        expect(summary["fail"]) == 0
        out.seek(0)
        report = out.read()
        # print("\n\n", report)
        expect(report).contains("just for testing")

    @test_that("todo decorator can be used to with a condition and descriptions explaining the todo reason which is printed near the test")
    def _(_):
        class MyTestCase:
            @test_that("todo test with description")
            @todo.when(True, "just for testing")
            def _(_):
                expect(True).is_falsy()

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        expect(result) == 0
        expect(summary["todo"]) == 1
        expect(summary["fail"]) == 0
        out.seek(0)
        report = out.read()
        # print("\n\n", report)
        expect(report).contains("just for testing")

    @test_that("A test can raise a fail by marking the test as todo during the test execution")
    @todo("")
    def _(_):
        fail("this feature not implemented yet")
        class MyTestCase:
            @test_that("todo test as todo")
            def _(_):
                xxx("just because")
                expect(True).is_falsy()

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        out.seek(0)
        report = out.read()
        expect(result) == 0
        expect(summary["total"]) == 1
        expect(summary["pass"]) == 0
        expect(summary["todo"]) == 1
        expect(report).contains("(reason: just because)")

if __name__ == "__main__":
    run()
