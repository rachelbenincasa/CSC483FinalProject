# CSC483FinalProject
Names: Cole Hersh, Rachel Benincasa, Bronson Housmans, and Shayden Lowry
Jeopardy

# Project Details
This is an IR system that uses a Jeopardy category and a question to find the answer.
The result is the return title of the document that most likely has the answer.  The dataset is a subset
of Wikipedia.  The report is attached to this repository as "CSC 483 Report.pdf".

# Requirements
- openAI
- whoosh
- SpaCy


# LLM Install and Use Instructions
1. Install LM Studio: https://lmstudio.ai/
2. Use Lm Studio to download Llama language model Llama-3.1-8B
3. Start server on Lm Studio to make LLM accessible
4. Run llama.py
   
Note: This will create a new directory called indexdir if it is not already present on your computer.
This may take a few minutes to run since the dataset is so large.

   
# The Probelem
You are given:
○ Wikipedia collection (280,715 articles; article == title + text)  <br> 
○ 100 questions  <br> 
● You have to retrieve the article (title) that is the answer to the question  <br> 
● Evaluation: % questions for which you get the correct answer (accuracy)  <br> 
● It is harder than it seems  <br> 
○ Your solution must be generic  <br> 
■ Don’t implement anything that is specific to the 100 questions  <br> 
■ It must work when the answer is any of the 280k articles  <br> 
○ Indexing 280k wikipedia articles is tricky  <br> 
■ ~123,221,423 tokens  <br> 
■ Preprocessing  <br> 
● Parsing the article  <br> 
● Tokenizing, stemming, and so on  <br> 
■ Do you index the whole thing?  <br> 
■ Lucene vs. your search engine  <br> 
○ Let’s look at the wikipedia articles  <br> 
