# CSC483FinalProject
Names: Cole Hersh, Rachel Benincasa, Bronson Housmans, and Shayden Lowry
Jeopardy

# Project Details
This is an IR system that uses a Jeopardy category and a question to find the answer.
The result is the return title of the document that most likely has the answer.  The dataset is a subset
of Wikipedia.  The report is attached to this repository as "CSC 483 Report.pdf".

#Requirements to install
openAI, whoosh, SpaCy


# LLM Install and Use Instructions
1. Install LM Studio: https://lmstudio.ai/
2. Use Lm Studio to download Llama language model Llama-3.1-8B
3. Start server on Lm Studio to make LLM accessible
4. Run llama.py

   
# The Probelem
You are given:
○ Wikipedia collection (280,715 articles; article == title + text)
○ 100 questions
● You have to retrieve the article (title) that is the answer to the question
● Evaluation: % questions for which you get the correct answer (accuracy)
● It is harder than it seems
○ Your solution must be generic
■ Don’t implement anything that is specific to the 100 questions
■ It must work when the answer is any of the 280k articles
○ Indexing 280k wikipedia articles is tricky
■ ~123,221,423 tokens
■ Preprocessing
● Parsing the article
● Tokenizing, stemming, and so on
■ Do you index the whole thing?
■ Lucene vs. your search engine
○ Let’s look at the wikipedia articles
