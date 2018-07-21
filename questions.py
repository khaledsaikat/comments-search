import json
from typing import Dict, List, Generator

import requests
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import CountVectorizer
from stopwords import stopwords

BASE_URL = "https://www.khanacademy.org"

QUESTIONS_URLS = ["https://www.khanacademy.org/api/internal/discussions/scratchpad/1981573965/questions?limit=500",
                  "https://www.khanacademy.org/api/internal/discussions/video/introduction-to-vectors-and-scalars/questions?limit=500",
                  "https://www.khanacademy.org/api/internal/discussions/video/making-webpages-intro/questions?limit=500",
                  "https://www.khanacademy.org/api/internal/discussions/video/atomic-weight-and-atomic-mass/questions?limit=500",
                  "https://www.khanacademy.org/api/internal/discussions/video/reading-pictographs/questions?limit=500"]


class Questions:
    """Handle questions"""
    request = None
    questions: List[Dict] = []
    indexName = "questions"

    def __init__(self):
        self.elasticsearch = Elasticsearch()

    def retrieve(self) -> List[Dict]:
        """Retrieve questions"""
        if self.questions:
            return self.questions

        for url in QUESTIONS_URLS:
            self.questions.extend(self.remove_empty_answers(self.retrieve_url(url)))
        return self.questions

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

    @staticmethod
    def remove_empty_answers(questions: Generator, size=100) -> List[Dict]:
        """Remove questions with empth answers and take first n questions"""
        return [question for question in questions if len(question["answers"]) > 0][:size]

    def retrieve_write_json(self):
        """Write retrieve questions"""
        data = {index: question for index, question in enumerate(self.retrieve())}
        self.write_json(data, "data/questions.json")

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
            # print(res)

    def clean_import(self):
        """Import questions to elastisearch and write to a json file"""
        self.store_to_elasticsearch()
        self.retrieve_write_json()
        data = {index: question["question"] for index, question in enumerate(self.retrieve())}
        self.write_json(data, "data/questions-only.json")

    def search(self, _query: str):
        """Search from elasticsearch"""
        _query = self.remove_stopwords(_query)
        print(_query)
        body = \
            {
                "query": {
                    "match": {
                        "question": {
                            "query": _query,
                            "operator": "and"
                        }
                    }
                },
                "highlight": {
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"],
                    "fields": {
                        "question": {}
                    }
                }
            }
        return self.elasticsearch.search(index=self.indexName, body=body)

    def combined_search(self, _query: str):
        _query = self.remove_stopwords(_query)
        results = self.search(_query)
        if results["hits"]["total"] > 0:
            return results

        queries = self.tokens_to_query(self.get_tokens(_query))
        scores = [self.search(new_query)["hits"]["max_score"] for new_query in queries]
        scores = [score if score else 0 for score in scores]
        #print(queries, scores)
        max_scores_index = scores.index(max(scores))
        return self.search(queries[max_scores_index])
        #return results

    def get_tokens(self, _text: str) -> List[str]:
        """Get tokens from a provided text. In our settings the method provide unigram tokens"""
        body = \
            {
                "field": "question",
                "text": _text
            }
        results = self.elasticsearch.indices.analyze(index=self.indexName, body=body)
        return [result["token"] for result in results["tokens"]]

    @staticmethod
    def remove_stopwords(text: str) -> str:
        """Remove stopwords from the query"""
        return " ".join([token for token in text.lower().split() if token not in stopwords])

    @staticmethod
    def tokens_to_query(tokens: List[str]):
        """get list of query with removing one token for each time"""
        queries = []
        for token in tokens:
            tokens_copy = tokens.copy()
            tokens_copy.remove(token)
            queries.append(" ".join(tokens_copy))
        return queries

    def search_result(self, query: str):
        """Show search result on console"""
        res = self.search(query)
        print("Got {} hits".format(res["hits"]["total"]))
        for index, hit in enumerate(res['hits']['hits']):
            print("{}. {}\n".format(index + 1, hit["_source"]["question"]))

    def result_ids(self, _query: str) -> List[int]:
        result = self.search(_query)
        return [item["_id"] for item in result["hits"]["hits"]] if result["hits"]["total"] > 0 else []

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
    # Questions().search_result("what")
    print(Questions().combined_search("difference1 between speed and velocity"))
    #print(Questions.tokens_to_query(['a', 'b', 'c', 'd']))
    # Questions().clean_import()
