import json
from typing import List

import numpy as np

from questions import Questions


class Evaluation:
    precision_recall_f1 = []

    def __init__(self, _query, _actual_ids):
        self.query = _query
        self.actual_ids: List[int] = list(map(int, _actual_ids))
        self.predicted_ids: List[int] = list(map(int, Questions().result_ids(_query)))

    @property
    def precision(self):
        if len(self.predicted_ids) == 0:
            return 0
        return len([_id for _id in self.predicted_ids if _id in self.actual_ids]) / len(self.predicted_ids)

    @property
    def recall(self):
        if len(self.actual_ids) == 0:
            return 0
        return len([_id for _id in self.actual_ids if _id in self.predicted_ids]) / len(self.actual_ids)

    @staticmethod
    def f1(_precision, _recall):
        if _precision + _recall == 0:
            return 0
        return 2 * (_precision * _recall) / (_precision + _recall)

    def result(self):
        _precision = self.precision
        _recall = self.recall
        _f1 = self.f1(_precision, _recall)
        Evaluation.precision_recall_f1.append((_precision, _recall, _f1))
        print("Query: {}".format(self.query))
        print("Precision: {}, Recall: {}, F1: {}".format(_precision, _recall, _f1))

    @staticmethod
    def mean_precision_recall_f1():
        data_matrix = np.array(Evaluation.precision_recall_f1)
        print("\nMean Precision: {}, Mean Recall: {}, Mean F1: {}\n".format(data_matrix[:, 0].mean(),
                                                                            data_matrix[:, 1].mean(),
                                                                            data_matrix[:, 2].mean()))

    @staticmethod
    def evaluate_json():
        with open("data/evaluate.json") as evaluate_file:
            evaluate_data = json.load(evaluate_file)
            for _query, _ids in evaluate_data.items():
                Evaluation(_query, _ids).result()


if __name__ == "__main__":
    Evaluation.evaluate_json()
    Evaluation.mean_precision_recall_f1()
