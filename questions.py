import json
from typing import Dict

import requests
from elasticsearch import Elasticsearch

QUESTIONS_URL = "https://www.khanacademy.org/api/internal/discussions/scratchpad/1981573965/questions?limit=20"


class Questions:
    request = None

    def __init__(self):
        self.elasticsearch = Elasticsearch()

    def retrieve(self):
        self.request = requests.get(QUESTIONS_URL)
        for feedback in self.request.json()["feedback"]:
            question = dict()
            question["question"] = feedback["content"]
            question["answers"] = [answer["content"] for answer in feedback["answers"]]
            yield question

    def retrieve_write_json(self):
        self.write_json({"questions": list(self.retrieve())}, "data/questions.json")

    @staticmethod
    def write_json(data: Dict, file_path: str):
        with open(file_path, "w") as json_file:
            json.dump(data, json_file)

    def store_to_elasticsearch(self):
        questions = self.retrieve()
        for index, question in enumerate(questions):
            res = self.elasticsearch.index(index="questions", doc_type="question", id=index, body=question)
            print(res)

    def search(self, query: str):
        body = {"query": {
            "match": {"question": query}
        }}
        return self.elasticsearch.search(index="questions", body=body)

    def search_result(self, query: str):
        res = self.search(query)
        print("Got {} hits".format(res["hits"]["total"]))
        for index, hit in enumerate(res['hits']['hits']):
            print("{}. {}\n".format(index + 1, hit["_source"]["question"]))


if __name__ == "__main__":
    Questions().search_result("what is parabola")
