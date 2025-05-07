from openai import OpenAI
import os
from searchJSON import Search_JSON
from jeopardy2 import Jeopardy2

class Llama:
    def __init__(self):
        # connect to local server
        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    def llm_process(self, val):
        """
        For input query we have the llm pick the best answer from the list of
        20 possible answers returned by the tf-idf pass.
        """
        completion = self.client.chat.completions.create(
            model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
            temperature=0.0,   # make results consistent
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Jeopardy expert.  The user will give you a Python "
                        "dict literal with keys 'Category', 'Question', and 'DocNames' "
                        "(a list of exactly 20 strings).  Pick the single best answer for"
                        "the given question "
                        "from that DocNames list. Return only the answer you have chosen. "
                        "Do not include any justification, contemplation, introduction, or any"
                        "words that are not simply your top pick from the 20 provided possible answers"
                        "any additional words that are not a single selection verbatim from the possible answers"
                        "will result in a disqualification of your jeapordy attempt."
                    )
                },
                {"role": "user", "content": val}
            ],
        )

        return completion.choices[0].message.content.strip()


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