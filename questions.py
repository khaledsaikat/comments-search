import json
from typing import Dict

import requests

QUESTIONS_URL = "https://www.khanacademy.org/api/internal/discussions/scratchpad/1981573965/questions"


class Questions:
    def __init__(self):
        self.request = requests.get(QUESTIONS_URL)

    def retrieve(self):
        for feedback in self.request.json()["feedback"]:
            question = dict()
            question["question"] = feedback["content"]
            question["answers"] = [answer["content"] for answer in feedback["answers"]]
            yield question

    def retreive_write_json(self):
        self.write_json({"questions": list(self.retrieve())}, "data/questions.json")

    @staticmethod
    def write_json(data: Dict, file_path: str):
        with open(file_path, "w") as json_file:
            json.dump(data, json_file)
