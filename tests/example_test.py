""" An example test suite to show how the reporting is done """

# Standard Imports

# Third Party Imports

# Internal Imports
from expect import expect, test_that, todo, skip, fail, execute, run, warn


class ExampleTestCase:
    @test_that("a passing test is reported as pass")
    def _(_):
        expect(True).is_truthy()

    @test_that("a test can be marked as skipped in which case it is not executed")
    @skip.when(True, "example")
    def _(_):
        fail("should not be executed")

    @test_that("a test can be skipped during the test execution")
    def _(_):
        skip("example")

    @test_that("a test can be marked as todo if it is expected to fail")
    @todo.when(True, "")
    def _(_):
        fail("not implemented")

    @test_that("a test can be marked as warning if it we do not consider the failure a real failure")
    @warn.when(True, "sdfdf")
    def _(_):
        fail("not implemented") 
        
    @test_that("a test can end up as warning with warn method during the execution")
    def _(_):
        warn("not implemented") 
        expect(True).is_truthy()

if __name__ == "__main__":
    result, counts = execute()
    