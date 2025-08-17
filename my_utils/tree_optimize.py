import numpy as np
import polars as pl
from hummingbird.ml import convert
from copy import deepcopy
import warnings
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, ExtraTreesClassifier, RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from tqdm import tqdm, trange
from rich import print

warnings.filterwarnings("ignore", category=UserWarning)
type TreeModel = ExtraTreesRegressor | RandomForestRegressor | ExtraTreesClassifier | RandomForestClassifier
type Tree = DecisionTreeRegressor | DecisionTreeClassifier


def optimize_trees(x: pl.DataFrame, y: pl.Series, model: TreeModel, hummingnize: bool = True) -> TreeModel:
    # Evaluate the score of each individual decision tree then order in descending order based on performance:
    num_trees: int = len(model)
    scores: list[float] = [0.0] * num_trees  # scores of individual decision trees

    print("Evaluating individual decision tree's performance...")
    for i, tree in tqdm(enumerate(model)):
        scores[i] = tree.score(x, y)

    ordered: np.ndarray = np.argsort(scores)[::-1].astype(np.uint16)  # order in descending order based on the performance of individual trees
    ordered_trees: list[Tree] = np.array(model.estimators_)[ordered].tolist()

    # Evaluate the scores of top-k decision trees then order them in descending order based on performance:
    scores: list[float] = [0.0] * (num_trees - 2)  # scores of the top-k decision trees (take at least take 2 trees)
    for k in trange(2, num_trees):
        tqdm.write(f"Evaluating top-{k} decision trees' performance...")
        m = deepcopy(model)  # create a new deepcopy of "model" not to alter the original model
        m.estimators_ = ordered_trees[:k]  # select the top "k" trees from "model"
        scores[k - 2] = m.score(x, y)

    top_k: np.ndarray = np.argsort(scores)[::-1].astype(np.uint16)  # order in descending order based on the performance of top-k decision trees

    mad: float = median_absolute_deviation(scores)
    best_k = top_k[0]  # best performing subset of top k-trees (not necessarily all the trees)
    top_score: float = scores[best_k]

    # To improve final model's generalization, we take highest number of trees without significant performance degradation:
    if best_k + 2 != num_trees:  # if we didn't select all trees:
        print("Bringing back some trees...")
        for i in tqdm(top_k[1:]):
            if i > best_k and top_score - scores[i] < mad:  # if we have less number of trees and the difference with the highest score is not significant (less than σ):
                best_k = i

    model.estimators_ = ordered_trees[: best_k + 2]
    return convert(model, "pytorch") if hummingnize else model


# @cython.cfunc  # declare as a C-level function; hence only visible internally and it's to be used within current module only
def median_absolute_deviation(arr: list[float]) -> float:  # declaring function's return type only works for C-level functions
    return 1.4826 * np.median(abs(arr - np.median(arr)))
