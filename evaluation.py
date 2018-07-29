import json
from typing import List, Dict
from collections import Counter

import numpy as np
from sklearn.metrics import cohen_kappa_score


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
        with open("data/evaluate1.json") as evaluate_file:
            evaluate_data = json.load(evaluate_file)
            for _query, _ids in evaluate_data.items():
                Evaluation(_query, _ids).result()


def combine_annotated_ids(annotated_ids: List[List[int]], min_similarity=2):
    """Combine annotated ids for a single query"""
    annotated_counter = Counter([id_ for single_set in annotated_ids for id_ in set(single_set)])
    return [pair[0] for pair in annotated_counter.most_common() if pair[1] >= min_similarity]


def indexing(valid: List[int], size=500):
    """Make sparse implementation with zeros"""
    zeros = np.zeros(size)
    for i in valid:
        zeros[i] = 1
    return zeros


def load_json_file(path):
    with open(path) as evaluate_file:
        return json.load(evaluate_file)


def merge_evaluate_files(file1, file2):
    data1 = load_json_file(file1)
    data2 = load_json_file(file2)

    keys = set(data1.keys()).intersection(set(data2.keys()))
    combined = {key: [] for key in set(keys)}

    [combined[k].append(v) for k, v in data1.items() if k in keys]
    [combined[k].append(v) for k, v in data2.items() if k in keys]

    return combined


def evaluate():
    combined = merge_evaluate_files("data/evaluate1.json", "data/evaluate2.json")
    evaluate_data = {}
    for question, answers in combined.items():
        print(question)
        #print(answers)
        cohen_kappa = cohen_kappa_score(indexing(answers[0]), indexing(answers[1]))
        print("cohen_kappa:", cohen_kappa)
        if cohen_kappa >= 0.5:
            common_ids = list(set.intersection(set(answers[0]), set(answers[1])))
            evaluate_data[question] = common_ids
            Evaluation(question, common_ids).result()



if __name__ == "__main__":
    #Evaluation.evaluate_json()
    evaluate()
    Evaluation.mean_precision_recall_f1()
