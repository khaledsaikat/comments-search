import json
from typing import Dict

import requests
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import CountVectorizer

QUESTIONS_URL = "https://www.khanacademy.org/api/internal/discussions/scratchpad/1981573965/questions?limit=100"


class Questions:
    """Handle questions from db"""
    request = None

    def __init__(self):
        self.elasticsearch = Elasticsearch()

    def retrieve(self):
        """Retrieve questions from url"""
        self.request = requests.get(QUESTIONS_URL)
        for feedback in self.request.json()["feedback"]:
            question = dict()
            question["question"] = feedback["content"]
            question["answers"] = [answer["content"] for answer in feedback["answers"]]
            yield question

    def retrieve_write_json(self):
        """Write retrieve questions"""
        self.write_json({"questions": list(self.retrieve())}, "data/questions.json")

    @staticmethod
    def write_json(data: Dict, file_path: str):
        """Write dict to json file"""
        with open(file_path, "w") as json_file:
            json.dump(data, json_file)

    def store_to_elasticsearch(self):
        """Store questions to elasticsearch"""
        questions = self.retrieve()
        for index, question in enumerate(questions):
            res = self.elasticsearch.index(index="questions", doc_type="question", id=index, body=question)
            print(res)

    def search(self, query: str):
        """Search from elasticsearch"""
        body = {"query": {
            "match": {"question": query}
        }}
        return self.elasticsearch.search(index="questions", body=body)

    def search_result(self, query: str):
        """Show search result on console"""
        res = self.search(query)
        print("Got {} hits".format(res["hits"]["total"]))
        for index, hit in enumerate(res['hits']['hits']):
            print("{}. {}\n".format(index + 1, hit["_source"]["question"]))

    def suggestions(self, query: str):
        """Generate suggestion for search input"""
        query_result = self.search(query)
        try:
            questions = [question["_source"]["question"] for question in query_result["hits"]["hits"][:5]]
            tokens = CountVectorizer(ngram_range=(1, 3)).fit(questions).get_feature_names()
            return [token for token in tokens if token.find(query) == 0]
        except Exception:
            return []


if __name__ == "__main__":
    Questions().search_result("what")
