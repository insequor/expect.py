from expect import expect, skip, test_that, todo  # type: ignore


class SampleTestCase:
    """Test the auto-generated class for NXOpen.CAE.SimSolution objects"""
    
    @classmethod
    def before_all(_):
        # logging.info("SampleTestCase.before_all")
        pass 

    @classmethod
    def after_all(_):
        # logging.info("  after_all")
        pass 

    def before(self):
        # logging.info("  before")
        pass 

    def after(self):
        # logging.info("  after")
        pass 

    @test_that("simple passing test")
    def _(_):
        expect(False).is_falsy()

    @test_that("a failing test with todo decorator is marked as TODO")
    @todo
    def _(_):
        expect(True).is_falsy()

    @test_that("a passing test with todo decorator is marked as fail")
    @todo
    def _(_):
        expect(False).is_falsy()

    @test_that("skip.when(True) should be skipped")
    @skip.when(True, "skip always")
    def _(_):
        expect(True).is_falsy()

    @test_that("skip.when(False) should not be skipped")
    @skip.when(False, "do not skip")
    def _(_):
        expect(False).is_falsy()

    @test_that("skip.when(lambda : True) should be skipped")
    @skip.when(lambda : True, "skip always but from callable")
    def _(_):
        expect(True).is_falsy()

    @test_that("skip.when(lambda : False) should not be skipped")
    @skip.when(lambda : False, "do not skip")
    def _(_):
        expect(False).is_falsy()

    @test_that("skip.unless(True) should not be skipped")
    @skip.unless(True, "do not skip")
    def _(_):
        expect(False).is_falsy()

    @test_that("skip.unless(False) should be skipped")
    @skip.unless(False, "skip always")
    def _(_):
        expect(False).is_falsy()

    @test_that("skip.unless(lambda: True) should not be skipped")
    @skip.unless(lambda: True, "do not skip")
    def _(_):
        expect(False).is_falsy()

    @test_that("skip.unless(lambda: False) should be skipped")
    @skip.unless(lambda: False, "skip always")
    def _(_):
        expect(False).is_falsy()
