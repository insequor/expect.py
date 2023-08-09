"""
    warn is introduced something similar to todo. Instead of marking a test as todo, it marks as warning
    But unlike todo, it does not trigger failure if the test passes
"""
# Standard Import
from io import StringIO 

# Third Party Imports 

# Internal Imports
from expect import expect, test_that, run, warn, fail


class WarningTestCase:
    @test_that("A failed test decorated with warning and condition is True reported as warning", tag="debug")
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

    @test_that("We can use a callable as a condition to warn")
    def _(_):
        class MyTestCase:
            @test_that("warning test")
            @warn.when(lambda: True, "condition to evaluate True")
            def _(_):
                fail("should be warning")

            @test_that("failing test")
            @warn.when(lambda: False, "condition to evaluate False")
            def _(_):
                fail("should not be warning")

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        expect(result) == 1
        expect(summary["total"]) == 2
        expect(summary["fail"]) == 1
        expect(summary["warning"]) == 1

    @test_that("We can use unless condition for warning")
    def _(_):
        class MyTestCase1:
            @test_that("warn test")
            @warn.unless(False, "")
            def _(_):
                fail("should be warning")

        out = StringIO()
        summary = {}
        result = run(MyTestCase1, out=out, summary=summary)
        expect(result) == 0
        expect(summary["total"]) == 1
        expect(summary["warning"]) == 1

        class MyTestCase2:
            @test_that("fail test")
            @warn.unless(True, "")
            def _(_):
                fail("should be failure")

        out = StringIO()
        summary = {}
        result = run(MyTestCase2, out=out, summary=summary)
        expect(result) == 1
        expect(summary["total"]) == 1
        expect(summary["fail"]) == 1
        

if __name__ == "__main__":
    run()
