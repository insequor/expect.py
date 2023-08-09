"""
    Testing the skip decorator
"""
# Standard Import
from io import StringIO 

# Third Party Imports 

# Internal Imports
from expect import expect, skip, test_that, run, fail

class SkipTestCase:
    @test_that("a test marked with skip decorator is reported as skip")
    def _(_):
        class MyTestCase:
            @test_that("todo test as todo")
            @skip.always("")
            def _(_):
                fail("")
                
        summary = {}
        result = run(MyTestCase, out=StringIO(), summary=summary)
        expect(result) == 0
        expect(summary["total"]) == 1
        expect(summary["skip"]) == 1

    @test_that("skip decorator can be used to with a condition and descriptions explaining the todo reason which is printed near the test")
    def _(_):
        class MyTestCase:
            @test_that("todo test with description")
            @skip.when(True, "just for testing")
            def _(_):
                fail("")

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        expect(result) == 0
        expect(summary["total"]) == 1
        expect(summary["skip"]) == 1
        out.seek(0)
        report = out.read()
        # print("\n\n", report)
        expect(report).contains("just for testing")

    @test_that("We can skip a test during the test execution")
    def _(_):
        class MyTestCase:
            @test_that("skip test")
            def _(_):
                skip("just because")
                fail("")

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        out.seek(0)
        report = out.read()
        expect(result) == 0
        expect(summary["total"]) == 1
        expect(summary["skip"]) == 1
        expect(report).contains("(reason: just because)")

    @test_that("We can use a callable as a condition for skip")
    def _(_):
        class MyTestCase:
            @test_that("skip test")
            @skip.when(lambda: True, "condition to evaluate True")
            def _(_):
                fail("should be warning")

            @test_that("failing test")
            @skip.when(lambda: False, "condition to evaluate False")
            def _(_):
                fail("should not be warning")

        out = StringIO()
        summary = {}
        result = run(MyTestCase, out=out, summary=summary)
        expect(result) == 1
        expect(summary["total"]) == 2
        expect(summary["skip"]) == 1
        expect(summary["fail"]) == 1


if __name__ == "__main__":
    run()
