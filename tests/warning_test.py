"""
    warn is introduced something similar to todo. Instead of marking a test as todo, it marks as warning
    But unlike todo, it does not trigger failure if the test passes
"""
# Standard Import
from io import StringIO 

# Third Party Imports 

# Internal Imports
from expect import expect, test_that, run, warn


class WarningTestCase:
    @test_that("A failed test decorated with warning and condition is True reported as warning")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            @warn.always("")
            def _(_):
                expect(True).is_falsy()

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        expect(result) == 0
        expect(summary["total"]) == 1
        expect(summary["pass"]) == 0
        expect(summary["warning"]) == 1

    @test_that("A warning decorator accepts a message and uses it in the test report")
    def _(_):
        class MyTestCase:
            @test_that("warning test with message")
            @warn.when(True, "just because")
            def _(_):
                expect(True).is_falsy()

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        out.seek(0)
        report = out.read()
        expect(result) == 0
        expect(summary["total"]) == 1
        expect(summary["pass"]) == 0
        expect(summary["warning"]) == 1
        expect(report).contains("(reason: just because)")

    @test_that("A failed test decorated with warning but condition is False, reported as failure")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            @warn.when(False)
            def _(_):
                expect(True).is_falsy()

        summary = {}
        result = run(MyTestCase, out=StringIO(), summary=summary)
        expect(result) == 1
        expect(summary["total"]) == 1
        expect(summary["pass"]) == 0
        expect(summary["fail"]) == 1

    @test_that("A test can raise a warning during the test execution which makes the test marked as warning")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            def _(_):
                warn("just because")
                expect(True).is_falsy()

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        out.seek(0)
        report = out.read()
        expect(result) == 0
        expect(summary["total"]) == 1
        expect(summary["pass"]) == 0
        expect(summary["warning"]) == 1
        expect(report).contains("(reason: just because)")


if __name__ == "__main__":
    run()
