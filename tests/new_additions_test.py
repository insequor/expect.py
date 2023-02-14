
from expect import expect, test_that, run 


class is_subclass_of_TestCase:
    @test_that("B is subclass of A if B is derived from B")
    def _(_):
        class A:
            pass 

        class B(A):
            pass 

        expect(B).is_subclass_of(A)

    @test_that("A is NOT subclass of B if B is derived from B")
    def _(_):
        class A:
            pass 

        class B(A):
            pass 

        def call():
            expect(A).is_subclass_of(B)
        expect(call).raises(AssertionError)

    @test_that("B is NOT subclass of A if B is NOT derived from B")
    def _(_):
        class A:
            pass 

        class B:
            pass 

        def call():
            expect(B).is_subclass_of(A)
        expect(call).raises(AssertionError)

class is_not_subclass_of_TestCase:
    @test_that("B is subclass of A if B is derived from B")
    def _(_):
        class A:
            pass 

        class B(A):
            pass 

        def call():
            expect(B).is_not_subclass_of(A)
        expect(call).raises(AssertionError)

    @test_that("A is NOT subclass of B if B is derived from B")
    def _(_):
        class A:
            pass 

        class B(A):
            pass 

        expect(A).is_not_subclass_of(B)
        
    @test_that("B is NOT subclass of A if B is NOT derived from B")
    def _(_):
        class A:
            pass 

        class B:
            pass 

        expect(B).is_not_subclass_of(A)
        

if __name__ == "__main__":
    run()
