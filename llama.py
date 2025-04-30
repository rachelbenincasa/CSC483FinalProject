from openai import OpenAI
import os
from searchJSON import Search_JSON
from jeopardy2 import Jeopardy2

class Llama:
    def __init__(self):
        # connect to local server
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    def llm_process(self, val, optimizer):
        completion = self.client.chat.completions.create(
            model = "NousResearch/Hermes-3-Llama-3.2-3B-GGUF",
            messages = [
                {"role" : "system", "content" : ("Return one document name that is the best answer for the given Category and Question. "
                "The format of the input is a dictionary with Category, Question, and DocNames "
                "as the keys. The DocNames key has the associated value of document names in an array."
                "You are only allowed to return one of the 20 document names present " +
                optimizer)},
                {"role" : "user", "content" : val}
            ],
            #tempearture = 0.7,
        )

        return completion.choices[0].message.content

def main():
    llm = Llama()
    jp = Jeopardy2()
    search_json = Search_JSON()
    # Create a directory for index
    if not os.path.exists("indexdir"):
        # print("json redo")
        # jp.process_json_files("json_output")
        # print("json done")
        os.mkdir("indexdir")
        search_json.build_index()
    # else:        
    #     in_cat = input("Enter a category: ")
    #     in_q = input("Enter a question: ")
    #     while in_cat != "exit":
    #         cat_str = ' '.join(jp.cleanup_text(in_cat))
    #         q_str = ' '.join(jp.cleanup_text(in_q))
    #         query = cat_str + " " + q_str
    #         search_json.search_index(query, llm, in_cat, in_q)
    #         in_cat = input("Enter a category: ")
    #         in_q = input("Enter a question: ")
    
    search_json.search_all(jp, llm)
main()