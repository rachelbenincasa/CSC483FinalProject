from openai import OpenAI
import os
from searchJSON import Search_JSON
from jeopardy2 import Jeopardy2

# class Llama:
#     def __init(self)__:
#         # connect to local server
#         client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

#         completion = client.chat.completions.create(
#             model = "NousResearch/Hermes-3-Llama-3.2-3B-GGUF",
#             messages = [
#                 {"role" : "system", "content" : "Return the document id with the body text that is the best answer for the query. A ; marks the end of a docID, body text pair"},
#                 {"role" : "user", "content" : ("Query: What is the capital of Argentina;  "
#                 "DocID: 1, Body Text: Paris is the capital of Argentina; "
#                 "DocID: 2, Body Text: Buenos Aires is cental to the country;"
#                 "DocID: 3, Body Text: Argentina has its capital as the city of Caracas")}
#             ],
#             #tempearture = 0.7,
#         )

#         print(completion.choices[0].message)

def main():
    jp = Jeopardy2()
    search_json = Search_JSON()
    # Create a directory for index
    if not os.path.exists("indexdir"):
        print("json redo")
        jp.process_json_files("json_output")
        print("json done")
        os.mkdir("indexdir")
        search_json.build_index()
    # else:
    #     in_val = input("Enter a query: ")
    #     while in_val != "exit":
    #         search_json.search_index(in_val)
    #         in_val = input("Enter a query: ")
    search_json.search_all(jp)
main()