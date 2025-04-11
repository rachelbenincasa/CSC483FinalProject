# CSC483FinalProject

Taken from slides:

The Proposal (2-3 pages)
● 1. General project idea (1-2 paragraphs). What will be the final outcome?
● 2. The problem: Define the problem in terms of the input and output (1-2
paragraphs including examples)
○ What problem you are going to solve (not how)
○ Include examples
○ This has nothing to do with the actual solutions: indexing
○ Do not answer how you are going to solve the problem yet
● 3. Dataset(s): Describe the data you will work with
○ How many examples?
○ Citation and source (link)
○ It needs to be readily available (downloadable); you do not have time to build a dataset
● 4. Baselines and Evaluation (1-2 paragraphs)
○ Define at least one baseline. A baseline is a model that is very simple
■ Homeworks
■ Choose randomly
○ Report results with the baseline in the proposal. Otherwise it will not be approved
■ Because if you don’t do better than the baseline you don’t have a decent project (at the
end)
● 5. Experiments and Results (2-3 paragraphs)
○ What is your proposed solution?
○ “I will replicate the solutions reported in paper X” is fine
○ Running code available in GitHub is not enough
■ If you can download the implementation, you do not credit for running it
■ Reusing and adapting code is fine, reading APIs and using them for your needs is fine



Jeopardy

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
