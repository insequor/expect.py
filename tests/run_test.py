"""
    Testing the todo decorator
"""
# Standard Imports
from io import StringIO
import re 

# Third Party Imports
import oktest 

# Internal Imports
from expect import expect, todo, test_that, run, fail, warn


class ExecuteTestCase:
    @test_that("running without any targets and no discovered tests leads to a report with 0 values")
    def _(_):                
        result = run(out=StringIO()) 
        expect(result) == 0

    @test_that("run returns the counts if the counts are requested")
    def _(_):
        summary = {}
        result = run(out=StringIO(), summary=summary) 
        expect(result) == 0
        expect(summary["total"]) == 0

    @test_that("summary contains the warning status we added")
    def _(_):
        summary = {}
        run(out=StringIO(), summary=summary) 
        expect(summary["warning"]) == 0

    @test_that("log summary run contains all values from the counts")
    def _(_):
        summary = {}
        out = StringIO()
        run(out=out, summary=summary) 
        out.seek(0)
        report = out.read()
        summary_ = {key: int(value) for (key, value) in re.findall(r"(\S+?):(\d+?)", report)}
        expect(summary) == summary_

    @test_that("run finds the tests from the given context and execute them all")
    def _(_):
        summary = {}

        class FirstTestCase:
            @test_that("pass")
            def _(_):
                pass 

            @test_that("fail")
            def _(_):
                fail("")

            @test_that("warning")
            @warn.always("")
            def _(_):
                fail("")

        class SecondTestCase:
            @test_that("pass")
            def _(_):
                pass 

            @test_that("fail")
            def _(_):
                fail("")

            
        run(out=StringIO(), summary=summary) 
        expect(summary["total"]) == 5

    @test_that("run accepts the TestCases given and ignores the others")
    def _(_):
        summary = {}

        class FirstTestCase:
            @test_that("pass")
            def _(_):
                pass 

            @test_that("fail")
            def _(_):
                fail("")

            @test_that("warning")
            @warn.always("")
            def _(_):
                fail("")

        class SecondTestCase:
            @test_that("pass")
            def _(_):
                pass 

            @test_that("fail")
            def _(_):
                fail("")

            
        run(SecondTestCase, out=StringIO(), summary=summary) 
        expect(summary["total"]) == 2
        

if __name__ == "__main__":
    run()
