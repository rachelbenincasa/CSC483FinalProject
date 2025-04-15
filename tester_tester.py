from tester import Tester

class IR:
    def __init__(self):
        self.name = "test"

    def run_query(self, query):
        return "Florida"

    def name(self):
        return self.name
test = Tester()
print("\033[91mThis is red text!\033[0m")

ir = IR()

test.test_accuracy(ir)

