"""
    warn is introduced something similar to todo. Instead of marking a test as todo, it marks as warning
    But unlike todo, it does not trigger failure if the test passes
"""
# Standard Import
from io import StringIO 

# Third Party Imports 

# Internal Imports
from expect import expect, todo, test_that, run, execute, warning, warn, skip


class WarningTestCase:
    @test_that("A passing test decorated with warning behaves like a passing test")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            @warning.when(True)
            def _(_):
                expect(True).is_truthy()

        result, counts = execute(MyTestCase, out=StringIO())
        expect(result) == 0
        expect(counts["total"]) == 1
        expect(counts["pass"]) == 1

    @test_that("A failed test decorated with warning and condition is True reported as warning")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            @warning
            def _(_):
                expect(True).is_falsy()

        out = StringIO()
        result, counts = execute(MyTestCase, out=out)
        expect(result) == 0
        expect(counts["total"]) == 1
        expect(counts["pass"]) == 0
        expect(counts["warning"]) == 1

    @test_that("A warning decorator accepts a message and uses it in the test report")
    def _(_):
        class MyTestCase:
            @test_that("warning test with message")
            @warning("just because")
            def _(_):
                expect(True).is_falsy()

        out = StringIO()
        result, counts = execute(MyTestCase, out=out)
        out.seek(0)
        report = out.read()
        expect(result) == 0
        expect(counts["total"]) == 1
        expect(counts["pass"]) == 0
        expect(counts["warning"]) == 1
        expect(report).contains("(reason: just because)")

    @test_that("A failed test decorated with warning but condition is False, reported as failure")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            @warning.when(False)
            def _(_):
                expect(True).is_falsy()

        result, counts = execute(MyTestCase, out=StringIO())
        expect(result) == 1
        expect(counts["total"]) == 1
        expect(counts["pass"]) == 0
        expect(counts["fail"]) == 1

    @test_that("A failed test decorated with warning and condition is True, reported as warning")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            @warning.when(True)
            def _(_):
                expect(True).is_falsy()

        result, counts = execute(MyTestCase, out=StringIO())
        expect(result) == 0
        expect(counts["total"]) == 1
        expect(counts["pass"]) == 0
        expect(counts["warning"]) == 1
        
    @test_that("A test can raise a warning during the test execution which makes the test marked as warning")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            def _(_):
                warn("just because")
                expect(True).is_falsy()

        out = StringIO()
        result, counts = execute(MyTestCase, out=out)
        out.seek(0)
        report = out.read()
        expect(result) == 0
        expect(counts["total"]) == 1
        expect(counts["pass"]) == 0
        expect(counts["warning"]) == 1
        expect(report).contains("(reason: just because)")


if __name__ == "__main__":
    run()
