
from expect import expect, test_that, run 


class Issue_2_EvaluatingConditionInPrintMessageTestCase:
    @test_that("Equality check performs the check only once if the values are equals")
    def _(_):
        class Provider:
            def __init__(self):
                self.callCount = 0
                self.value = 2.0

            def __eq__(self, other):
                print(f"\n Value is requested: {self.callCount}")
                self.callCount += 1
                return self.value == other

            def __ne__(self, other):
                print(f"\n Value is requested: {self.callCount}")
                self.callCount += 1
                return self.value != other

        provider = Provider()
        expect(provider) == 2.0
        expect(provider.callCount) == 1


if __name__ == "__main__":
    run()
