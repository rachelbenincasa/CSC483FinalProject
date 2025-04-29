import re
import spacy
from pathlib import Path
import math
import collections
import json
import os

class Jeopardy2:
    def __init__(self):
        # uses NLTK stop words found on github
        self.stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", 
                           "you", "your", "yours", "yourself", "yourselves", "he", 
                           "him", "his", "himself", "she", "her", "hers", "herself", 
                           "it", "its", "itself", "they", "them", "their", "theirs", 
                           "themselves", "what", "which", "who", "whom", "this", "that", 
                           "these", "those", "am", "is", "are", "was", "were", "be", 
                           "been", "being", "have", "has", "had", "having", "do", "does", 
                           "did", "doing", "a", "an", "the", "and", "but", "if", "or", 
                           "because", "as", "until", "while", "of", "at", "by", "for", 
                           "with", "about", "against", "between", "into", "through", 
                           "during", "before", "after", "above", "below", "to", "from", 
                           "up", "down", "in", "out", "on", "off", "over", "under", 
                           "again", "further", "then", "once", "here", "there", "when", 
                           "where", "why", "how", "all", "any", "both", "each", "few", 
                           "more", "most", "other", "some", "such", "no", "nor", "not", 
                           "only", "own", "same", "so", "than", "too", "very", "s", "t", 
                           "can", "will", "just", "don", "should", "now"]
        self.articles = {}
        self.docVectors = {}
        self.id_to_title = {}
        self.nlp = spacy.load('en_core_web_sm')
        self.i = 109524

    def cleanup_text(self, text):
        text = text.lower()
        # remove punc
        text = re.sub(r'[^\w\s]', '', text)
        # remove category ==
        text = re.sub(r'==', '', text)
        # remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        # remove tabs, underline, italic, newline
        text = re.sub(r'\\[utn]', '', text)
        # lemmatization and stop word removal
        doc = self.nlp(text)
        words = [token.lemma_ for token in doc if token.lemma_ not in self.stop_words 
                 and len(token.lemma_.strip()) > 0 and "\n" not in token.lemma_]
        return words
        
    def add_article(self, original_title, original_text):
        # adds the specific article to the articles dictionary
        self.articles[self.i] = {
        'original_title': original_title,
        'cleaned_text': self.cleanup_text(original_text)
        }
        self.i += 1

    def print_sample_articles(self, n=5):
        for i, article in self.articles.items():
            print(f"\n--- Article {i + 1} ---")
            print(f"Original Title: {article['original_title']}")
            print(f"Cleaned Text (first 20 words): {article['cleaned_text'][:20]}")

    def load_articles_from_dir(self, dir_path):
        path = Path(dir_path)
        json_path = Path("json_output")
        json_file_num = 0
        first = True
        # use a JSON file to save dictionary created from each wiki file in array of dicts
        # with open(output_path, 'a') as out:
        #     out.write('[')
        
        for file_path in path.glob('*.txt'):
            if json_file_num > 73:
                print(f"Processing {file_path}")
                with(json_path / f'output{json_file_num}.json').open('a', encoding='utf-8') as f:
                    f.write('[')
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_title = None
                    current_text = []

                    for line in f:
                        # clear articles dict
                        self.articles = {}
                        line = line.strip()

                        # Check for a new article
                        match = re.match(r'\[\[(.+?)\]\]', line)
                        if match:
                        # Save the previous article if valid
                            if current_title and current_text:
                                full_text = '\n'.join(current_text)
                                self.add_article(current_title, full_text)
                                # append articles dict to json array
                                with(json_path / f'output{json_file_num}.json').open('a', encoding='utf-8') as f:
                                    json.dump(self.articles, f, indent=2)
                                    f.write(",\n")

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
                        # save articles dict to json file
                        with(json_path / f'output{json_file_num}.json').open('a', encoding='utf-8') as f:
                            json.dump(self.articles, f, indent=2)
                
                with(json_path / f'output{json_file_num}.json').open('a', encoding='utf-8') as f:
                    f.write(']')
            json_file_num += 1

    ### TF-IDF STUFF (LNC LTN TFIDF FROM LAST PROJECT):

    def build_tfidf_index(self):
        print("\nBuilding tfidf index...\n\n")
        N = self.i
        json_path = Path("json_output")

        for file_path in json_path.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for i in range(len(data)):
                for doc_id, article in data[i].items():
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
        N = self.i

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
        json_path = Path("json_output")

        for file_path in json_path.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for i in range(len(data)):
                for article in data[i].values():
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

    def clean_data(self, arr):
        cleaned = []
        for word in arr:
            # Make sure it's a non-empty string
            if not isinstance(word, str) or not word.strip():
                continue
            
            word = word.strip()

            # Apply multiple conditions
            if len(word) < 2 or len(word) > 20:  # Skip very short words
                continue
            if '\\' in word:
                continue
            if isinstance(word, str) and any(c.isalpha() for c in word) and any(c.isdigit() for c in word):
                continue

            # If word passes all checks, keep it
            cleaned.append(word)

        return cleaned

    def process_json_files(self, directory):
        json_path = Path(directory)
        
        for file_path in json_path.glob('*.json'):
            print(f"Processing {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # data is a list of dicts (based on your description)
            new_data = []
            for entry in data:
                new_entry = {}
                for key, value in entry.items():
                    # value is expected to be a dictionary
                    if isinstance(value, dict):
                        value['cleaned_text'] = self.clean_data(value['cleaned_text'])
                    new_entry[key] = value
                new_data.append(new_entry)

            # After processing, write back to SAME FILE
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)


# def main():
#     jp = Jeopardy2()
#     jp.load_articles_from_dir("wiki-subset-files")
#     print(f"Loaded {len(jp.articles)} articles.")
#     # jp.print_sample_articles()

#     jp.build_tfidf_index()

#     # Evaluate accuracy on the file for various TFIDF return set sizes:
#     for i in [1, 20, 50, 100, 250]:
#         jp.evaluate_from_file("questions.txt", i)
# main()