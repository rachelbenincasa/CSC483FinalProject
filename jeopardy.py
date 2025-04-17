import re
from pathlib import Path
import json
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Jeopardy:
  def __init__(self, ngram_range=(1, 2)):
    self.stop_words = {'the', 'and', 'of', 'to', 'in', 'a', 'is', 'that', 'for'}
    self.articles = []
    self.vectorizer = TfidfVectorizer(ngram_range=ngram_range)
    self.tfidf_matrix = None

  def cleanup_text(self, text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = [word for word in text.split() if word not in self.stop_words]
    return ' '.join(words)

  def add_article(self, original_title, original_text):
    cleaned_title = self.cleanup_text(original_title)
    cleaned_text = self.cleanup_text(original_text)
    self.articles.append({
        'original_title': original_title,
        'cleaned_title': cleaned_title,
        'original_text': original_text,
        'cleaned_text': cleaned_text
    })


    def load_articles_from_folder(self, folder_path):
        for file in Path(folder_path).iterdir():
            if file.suffix == '.txt':
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()

                entries = re.split(r'\[\[(.*?)\]\]', content)
                for i in range(1, len(entries), 2):
                    title = entries[i].strip()
                    text = entries[i + 1].strip()

                    if 'redirect' in text.lower():
                        continue
                    self.add_article(title, text)

    def compute_tfidf(self):
        texts = [article['cleaned_text'] for article in self.articles]
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)


    def query(self, query_text, top_n=20):
        if self.tfidf_matrix is None:
            raise ValueError("TF-IDF not computed. Run compute_tfidf() first.")

        cleaned_query = self.cleanup_text(query_text)
        query_vec = self.vectorizer.transform([cleaned_query])
        scores = np.dot(self.tfidf_matrix, query_vec.T).toarray().ravel()

        top_indices = scores.argsort()[::-1][:top_n]
        results = [(self.articles[i]['original_title'], scores[i]) for i in top_indices]
        return results

      

