import re
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
      'cleaned_text': self.cleanup.text(original text)
    })


    # method to call add_article for each article name and text
    # need to go through each wiki-subset-files and call it for each one


    # method to use td-idf and return the top 20 or so results


    # method to use a language model to get the best result
      

