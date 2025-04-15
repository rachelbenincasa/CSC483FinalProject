'''
Author: Cole Hersh
Description: this file compares the output of an IR System
to the expected answer and calculates its accuracy
'''


class Tester:
    '''
    Sets up the globals
    query_answer - a dictionary where the key is a 2-tuple
    where the first element is the category and the 2nd is the question.
    The value is the answer
    '''
    def __init__(self):
        self.query_answer = {}
        self.file = "questions.txt"
        self.setup()
        self.print_dict()

    '''
    populates query_answer
    '''
    def setup(self):
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

    '''
    prints query_answer for testing purposes
    '''
    def print_dict(self):
        for key, value in self.query_answer.items():
            print("Catagory: ", key[0], "\nQuestion: ", key[1], "\nAnswer:",
                  self.query_answer[key], "\n\n\n")


