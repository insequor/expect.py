"""
    Testing the todo decorator
"""
# Standard Imports
from io import StringIO
import re 

# Third Party Imports
import oktest 

# Internal Imports
from expect import expect, todo, test_that, run, execute


class ExecuteTestCase:
    @test_that("running without any targets and no discovered tests leads to a report with 0 values")
    def _(_):                
        result, counts = execute(out=StringIO()) 
        expect(result) == 0
        expect(counts["total"]) == 0


if __name__ == "__main__":
    run()
