import re
import math
import collections
from pathlib import Path
import json
from collections import defaultdict

class Jeopardy:
  def __init__(self):
    # stop words to remove
    self.stop_words = {'the', 'and', 'of', 'to', 'in', 'a', 'is', 'that', 'for'}
    # articles will store (for each article)
    # -original title 
    # -cleaned title
    # -original text
    # -cleaned text
    self.articles = []
    self.docVectors = {}  # for tf idf
    self.id_to_title = {}

  def cleanup_text(self, text):
    # lowercase
    text = text.lower()
    # remove punc
    text = re.sub(r'[^\w\s]', '', text)
    # split into words & remove any stop words
    words = [word for word in text.split() if word not in self.stop_words]
    return words

  def add_article(self, original_title, original_text):
    # adds the specific article to the articles dictionary
    self.articles.append({
      'original_title': original_title,
      'cleaned_title': self.cleanup_text(original_title),
      'original_text': original_text,
      'cleaned_text': self.cleanup_text(original_text)
    })

  def print_sample_articles(self, n=5):
    for i, article in enumerate(self.articles[:n]):
      print(f"\n--- Article {i + 1} ---")
      print(f"Original Title: {article['original_title']}")
      print(f"Cleaned Title: {article['cleaned_title']}")
      print(
        f"Original Text (first 200 chars): {article['original_text'][:200]}")
      print(f"Cleaned Text (first 20 words): {article['cleaned_text'][:20]}")

  def load_articles_from_dir(self, dir_path):
      path = Path(dir_path)
      for file_path in path.glob('*.txt'):
        print(f"Processing {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
          current_title = None
          current_text = []

          for line in f:
            line = line.strip()

            # Check for a new article
            match = re.match(r'\[\[(.+?)\]\]', line)
            if match:
              # Save the previous article if valid
              if current_title and current_text:
                full_text = '\n'.join(current_text)
                self.add_article(current_title, full_text)

              # Start a new article
              current_title = match.group(1)
              current_text = []
              continue

            # Skip redirect articles
            if line.lower().startswith("#redirect"):
              # Invalidate the current article
              current_title = None
              current_text = []
              continue

            current_text.append(line)

          # Save last article in file
          if current_title and current_text and not current_text[0].startswith(
                  "#REDIRECT"):
            full_text = '\n'.join(current_text)
            self.add_article(current_title, full_text)

### TF-IDF STUFF (LNC LTN TFIDF FROM LAST PROJECT):

  def build_tfidf_index(self):
        print("\nBuilding tfidf index...\n\n")
        N = len(self.articles)
        for doc_id, article in enumerate(self.articles):
            terms = article['cleaned_text']
            term_counts = collections.Counter(terms)

            vector = {}
            sum_of_squares = 0

            for term, tf in term_counts.items():
                weight = 1 + math.log10(tf)
                vector[term] = weight
                sum_of_squares += weight ** 2

            denom = math.sqrt(sum_of_squares)
            if denom > 0:
                for term in vector:
                    vector[term] /= denom

            self.docVectors[doc_id] = vector
            self.id_to_title[doc_id] = article['original_title']

  def query(self, question, returned_set_size):
        terms = self.cleanup_text(question)
        q_counts = collections.Counter(terms)
        query_vector = {}
        N = len(self.docVectors)

        # Compute tf-idf weights for query
        for term, tf in q_counts.items():
            tf_weight = 1 + math.log10(tf)
            df = sum(1 for doc in self.docVectors.values() if term in doc)
            if df > 0:
                idf = math.log10(N / df)
                query_vector[term] = tf_weight * idf

        # Score documents
        scores = {}
        for doc_id, doc_vector in self.docVectors.items():
            score = 0
            for term, q_weight in query_vector.items():
                if term in doc_vector:
                    score += q_weight * doc_vector[term]
            scores[doc_id] = score

        # Sort by score
        top_docs = sorted(scores.items(), key=lambda x: -x[1])[:returned_set_size]  # change this [:V] variable to change size of set returned
        return [self.id_to_title[doc_id] for doc_id, _ in top_docs]


# TESTING TO SEE IF CORRECT ANSWERS ARE RETURNED BY TFIDF OR ARE EVEN IN DATASET:

  def title_in_dataset(self, answer):
    answer = answer.lower().strip()
    for article in self.articles:
      if answer == article['original_title'].lower().strip():
        return True
    return False

  def evaluate_from_file(self, filepath, tfidf_set_size):
    with open(filepath, 'r', encoding='utf-8') as f:
      lines = [line.strip() for line in f if line.strip()]

    assert len(
      lines) % 3 == 0, "File should have triplets of Category, Question, Answer"

    total = 0
    hits = 0
    not_in_set = 0
    problematic_questions = []

    for i in range(0, len(lines), 3):
      category = lines[i]
      question = lines[i + 1]
      answers = [a.strip().lower() for a in
                 lines[i + 2].split('|')]  # support multiple answers

      query = f"{category} {question}"

      top_titles = self.query(query, tfidf_set_size)
      top_titles_lower = [t.lower() for t in top_titles]

      # Check if any answer is in dataset
      answer_in_dataset = any(self.title_in_dataset(ans) for ans in answers)
      #print("\nExpected answer is in data set?:")
      #print(answer_in_dataset)

      if not answer_in_dataset:
        not_in_set += 1
        problematic_questions.append({
          "category": category,
          "question": question,
          "answers": answers
        })


      total += 1
      if any(ans in top_titles_lower for ans in answers):
        hits += 1
        """
        print(
          f"\n HIT!!!***!!!***!!: {query}\nExpected: {answers}\nGot: {top_titles[:5]}")
      else:
        print(
          f"\n Missed: {query}\nExpected: {answers}\nGot: {top_titles[:5]}")
        """

    print(f"\n Hit rate: {hits}/{total} = {hits / total:.2%}   TFIDF Returnes top {tfidf_set_size} results")

    print(f"Answers not in dataset: {not_in_set}/{total}")

    if problematic_questions:
        print("\nQuestions with answers not found in dataset:")
        for item in problematic_questions:
            print(f" - [{item['category']}] {item['question']} — Expected: {item['answers']}")
###


jp = Jeopardy()
jp.load_articles_from_dir("wiki-subset-files")
print(f"Loaded {len(jp.articles)} articles.")
jp.print_sample_articles()

jp.build_tfidf_index()

# Evaluate accuracy on the file for various TFIDF return set sizes:
for i in [1, 500, 1000, 2500, 5000, 10000]:
    jp.evaluate_from_file("questions.txt", i)


"""
while True:
    q = input("Jeopardy question: ").strip()
    if q.lower() == "exit":
        break
    results = jp.query(q)
    for i, title in enumerate(results, 1):
        print(f"{i}. {title}")
"""