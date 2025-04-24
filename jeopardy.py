import re
import math
import collections
from pathlib import Path
import json
from collections import defaultdict

class Jeopardy:
    def __init__(self):
        # stop words to remove
        self.stop_words = {'a', 'an', 'the',
        'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'can', 'could', 'shall', 'should',
        'of', 'to', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'up', 'down',
        'about', 'into', 'over', 'under', 'after', 'before', 'between',
        'and', 'or', 'but', 'if', 'because', 'as', 'while', 'until',
        'not', 'there', 'here', 'when', 'where', 'how', 'why', 'what', 'which', 'who',
        'whom', 'whose', 'some', 'any', 'all', 'many', 'few', 'most', 'other',
        }
        # articles will store (for each article)
        # -original title
        # -cleaned title
        # -original text
        # -cleaned text
        # -metadata (for JSON files)
        self.articles = []
        self.docVectors = {}  # for tf idf
        self.id_to_title = {}
        self.title_to_article = {}  # dictionary for quick title lookup

    def cleanup_text(self, text):
        # lowercase
        text = text.lower()
        # remove punc
        text = re.sub(r'[^\w\s]', '', text)
        # split into words & remove any stop words
        words = [word for word in text.split() if word not in self.stop_words]
        return words

    def add_article(self, article_data):
        """Add an article from either text data or JSON data"""
        if isinstance(article_data, dict):
            # JSON data case
            original_title = article_data.get('title', '')
            original_text = article_data.get('text', '')
            metadata = article_data.get('metadata', {})
        else:
            # Original text data case (tuple)
            original_title, original_text = article_data
            metadata = {}

        self.articles.append({
            'original_title': original_title,
            'cleaned_title': self.cleanup_text(original_title),
            'original_text': original_text,
            'cleaned_text': self.cleanup_text(original_text),
            'metadata': metadata
        })

        # Add to title lookup dictionary
        if original_title:
            self.title_to_article[original_title.lower()] = self.articles[-1]

    def print_sample_articles(self, n=5):
        for i, article in enumerate(self.articles[:n]):
            print(f"\n--- Article {i + 1} ---")
            print(f"Original Title: {article['original_title']}")
            print(f"Cleaned Title: {article['cleaned_title']}")
            print(f"Original Text (first 200 chars): {article['original_text'][:200]}")
            print(f"Cleaned Text (first 20 words): {article['cleaned_text'][:20]}")
            if article['metadata']:
                print(f"Metadata: {article['metadata']}")

    def load_articles_from_dir(self, dir_path):
        """Load articles from directory, automatically detecting JSON or text files"""
        path = Path(dir_path)

        # First try loading JSON files
        json_files = list(path.glob('*.json'))
        if json_files:
            self.load_articles_from_json_dir(dir_path)
            return

        # Fall back to text files if no JSON files found
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
                            self.add_article((current_title, full_text))

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
                if current_title and current_text and not current_text[0].startswith("#REDIRECT"):
                    full_text = '\n'.join(current_text)
                    self.add_article((current_title, full_text))

    def load_articles_from_json_dir(self, dir_path):
        """Load articles from JSON files in a directory"""
        path = Path(dir_path)
        for json_file in path.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Handle both single article and lists of articles
                    if isinstance(data, list):
                        for article in data:
                            self.add_article(article)
                    else:
                        self.add_article(data)

            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Error loading {json_file}: {e}")
                continue

        print(f"Loaded {len(self.articles)} articles from JSON files")

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
        top_docs = sorted(scores.items(), key=lambda x: -x[1])[:returned_set_size]
        return [self.id_to_title[doc_id] for doc_id, _ in top_docs]

    def title_in_dataset(self, answer):
        answer = answer.lower().strip()
        # Use the dictionary for faster lookup
        return answer in self.title_to_article

    def evaluate_from_file(self, filepath, tfidf_set_size):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        assert len(lines) % 3 == 0, "File should have triplets of Category, Question, Answer"

        total = 0
        hits = 0
        not_in_set = 0
        problematic_questions = []

        for i in range(0, len(lines), 3):
            category = lines[i]
            question = lines[i + 1]
            answers = [a.strip().lower() for a in lines[i + 2].split('|')]  # support multiple answers

            query = f"{category} {question}"

            top_titles = self.query(query, tfidf_set_size)
            top_titles_lower = [t.lower() for t in top_titles]

            # Check if any answer is in dataset
            answer_in_dataset = any(self.title_in_dataset(ans) for ans in answers)

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

        print(f"\nHit rate: {hits}/{total} = {hits / total:.2%}   TFIDF Returns top {tfidf_set_size} results")
        print(f"Answers not in dataset: {not_in_set}/{total}")

        if problematic_questions:
            print("\nQuestions with answers not found in dataset:")
            for item in problematic_questions:
                print(f" - [{item['category']}] {item['question']} — Expected: {item['answers']}")


# Main execution
if __name__ == "__main__":
    jp = Jeopardy()
    jp.load_articles_from_dir("wiki-subset-files")
    print(f"Loaded {len(jp.articles)} articles.")
    jp.print_sample_articles()

    jp.build_tfidf_index()

    # Evaluate accuracy on the file for various TFIDF return set sizes:
    for i in [1, 500, 1000, 2500, 5000, 10000]:
        jp.evaluate_from_file("questions.txt", i)

    # Interactive query mode
    while True:
        q = input("\nJeopardy question (or 'exit' to quit): ").strip()
        if q.lower() == "exit":
            break
        results = jp.query(q, 10)  # Show top 10 results
        for i, title in enumerate(results, 1):
            print(f"{i}. {title}")