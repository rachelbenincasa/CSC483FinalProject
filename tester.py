"""
Author: Cole Hersh
Description: this file compares the output of an IR System
to the expected answer and calculates its accuracy.
The results are written to both the terminal and a file with a
unique name so the results of different IR systems can be compared.
"""


class Tester:
    """
    Sets up the globals
    query_answer - a dictionary where the key is a 2-tuple
    where the first element is the category and the 2nd is the question.
    The value is the answer
    """
    def __init__(self):
        self.query_answer = {}
        self.file = "questions.txt"
        self.setup()
        self.print_dict()


    def setup(self):
        """
        populates query_answer
        """
        file = open(self.file, "r")
        counter = 0
        cat = ""
        question = ""
        for line in file:
            line = line.strip()
            if line == "":
                continue
            elif counter == 0:
                cat = line
                counter += 1
            elif counter == 1:
                question = line
                counter += 1
            else:
                self.query_answer[(cat, question)] = line
                counter = 0


    def print_dict(self):
        """
        prints query_answer for testing purposes
        """
        for key, value in self.query_answer.items():
            print("Catagory: ", key[0], "\nQuestion: ", key[1], "\nAnswer:",
                  self.query_answer[key], "\n\n\n")


    def test_accuracy(self, ir_system):
        """
        gets the accuracy and writes the results to a file
        """
        correct = 0
        count = 0
        write = open("tester_output\\results-" + ir_system.name, 'w')
        for key, value in self.query_answer.items():
            count += 1
            curr_string = 'Testing Query: ' + key[1] + '\n'
            print(curr_string)
            results = ir_system.run_query(key[1])

            if results != self.query_answer[key]:
                error_string = "\033[91mIncorrect Result\033[0m\n"
                error_string += "Expected: " + self.query_answer[key]  + " "
                error_string += "Got: " + results + "\n\n"

                print(error_string)
                curr_string += error_string
            else:
                curr_string += "PASSED\n\n"
                correct += 1
            write.write(curr_string)

        print("==========================================")
        print("Correct:", correct)
        print("Incorrect:", count - correct)
        print("Queries:", count)
        print("Accuracy: " + str(correct/count) + "%")
        print("==========================================")

        write.write("==========================================\n")
        write.write("Correct: " + str(correct) + "\n")
        write.write("Incorrect: " + str(count - correct) + "\n")
        write.write("Queries: " + str(count) + "\n")
        write.write("Accuracy: " + str(correct/count) + "%\n")
        write.write("==========================================\n")
