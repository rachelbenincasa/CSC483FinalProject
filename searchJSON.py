import json
from pathlib import Path
from whoosh import scoring
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, ID, TEXT
from whoosh.qparser import QueryParser, OrGroup
from whoosh.analysis import StemmingAnalyzer

class Search_JSON:
    def __init__(self):
        self.schema = Schema(
            doc_id=ID(stored=True),
            doc_name=TEXT(stored=True),
            text=TEXT(stored=True)
        )

    def build_index(self):
        print("Building index")
        ix = create_in("indexdir", self.schema)
        writer = ix.writer()
        json_path = Path("json_output")
        for file_path in json_path.glob('*.json'):
            print(str(file_path))
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                for key, value in item.items():
                    arr_join = ' '.join(value['cleaned_text']).replace("\n", " ").strip()
                    writer.add_document(
                        doc_id=key,
                        doc_name=value['original_title'],
                        text=arr_join
                    )
        writer.commit()
        print("Completed index")

    def search_index(self, input):
        ix = open_dir("indexdir")
        og = OrGroup.factory(0.9)

        # Customize BM25F scoring
        custom_bm25f = scoring.BM25F(
            k1=1.5,               # try tuning from 1.2 to 2.0
            B=0.7,                # try tuning from 0.5 to 1.0
            field_B={"text": 0.7, "doc_name": 0.3},
            field_boosts={"text": 1.2, "doc_name": 0.8}
)

        with ix.searcher(weighting=custom_bm25f) as searcher:
            parser = QueryParser("text", ix.schema, group=og)
            query = parser.parse(input)
            results = searcher.search(query, limit=20)

            res_arr = []
            for hit in results:
                recovered_doc = {
                    "original_title": hit["doc_name"],
                    "cleaned_text": hit["text"]
                }
                res_arr.append(recovered_doc)
            # for dict in res_arr:
            #     print(dict['original_title'])
            return res_arr
        
    def search_all(self, jp):
        with open('questions.txt', 'r', encoding='utf-8') as f:
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

            cat_str = ' '.join(jp.cleanup_text(category))
            q_str = ' '.join(jp.cleanup_text(question))
            query = cat_str + " " + q_str
            print("Query: " + query)
            ans = self.search_index(query)

            for dict in ans:
                if dict['original_title'].lower() in answers:
                    hits += 1
                    break
            total += 1
        print(f"\n Hit rate: {hits}/{total} = {hits / total:.2%}   TFIDF Returns top 20 results")

        # 53% for unfiltered question only
        # 56% for filtered question only
        # 62% for filtered category AND filtered question