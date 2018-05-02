import json
from typing import Dict, List

import requests
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import CountVectorizer

BASE_URL = "https://www.khanacademy.org"
QUESTIONS_URLS = ["https://www.khanacademy.org/api/internal/discussions/scratchpad/1981573965/questions?limit=10",
                  "https://www.khanacademy.org/api/internal/discussions/scratchpad/1981573965/questions?limit=10"]


class Questions:
    """Handle questions"""
    request = None

    def __init__(self):
        self.elasticsearch = Elasticsearch()

    def retrieve(self) -> List[Dict]:
        """Retrieve questions"""
        questions = []
        for url in QUESTIONS_URLS:
            questions.extend(list(self.retrieve_url(url)))
        return self.remove_duplicate(questions)

    @staticmethod
    def remove_duplicate(questions: List[Dict]) -> List[Dict]:
        return list({question["key"]: question for question in questions}.values())

    def retrieve_url(self, url: str):
        """Retrieve questions from provided url"""
        self.request = requests.get(url)
        for feedback in self.request.json()["feedback"]:
            question = dict()
            question["question"] = feedback["content"]
            question["answers"] = [answer["content"] for answer in feedback["answers"]]
            question["url"] = BASE_URL + feedback["permalink"]
            question["key"] = feedback["key"]
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
        print("Questions count: ", len(questions))
        for index, question in enumerate(questions):
            res = self.elasticsearch.index(index="questions", doc_type="_doc", id=index, body=question)
            print(res)

    def search(self, _query: str):
        """Search from elasticsearch"""
        body = {"query": {
            "match": {"question": {"query": _query, "operator": "and"}}
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
    #Questions().search_result("what")
    Questions().store_to_elasticsearch()
