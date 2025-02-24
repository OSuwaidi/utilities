import numpy as np
import polars as pl
from hummingbird.ml import convert
from copy import deepcopy
import warnings
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, ExtraTreesClassifier, RandomForestClassifier
from tqdm import tqdm, trange
from rich import print

warnings.filterwarnings("ignore", category=UserWarning)
type TreeModel = ExtraTreesRegressor | RandomForestRegressor | ExtraTreesClassifier | RandomForestClassifier


# @cython.locals(i=cython.size_t)
def optimize_trees(x: pl.DataFrame, y: pl.Series, model: TreeModel, hummingnize: bool = True) -> TreeModel:
    # Evaluate the score of each individual decision tree then order in descending order based on performance:
    scores: list[float] = [0.0] * len(model)  # scores of individual decision trees
    print("Evaluating individual decision tree's performance...")
    for i, m in tqdm(enumerate(model)):
        scores[i] = m.score(x, y)
    order: np.ndarray = np.argsort(scores)[::-1].astype(np.uint16)  # order in descending order based on the performance of individual trees

    # Evaluate the scores of top-k decision trees then order them in descending order based on performance:
    num_trees: int = len(model) - 1  # we will at least take 2 trees (0th index -> top 2 trees, 1st -> top 3 trees, etc.)
    scores: list[float] = [0.0] * num_trees  # scores of the top-k decision trees
    for i in trange(num_trees):
        tqdm.write(f"Evaluating top-{i + 2} decision trees' performance...")
        m = deepcopy(model)  # create a new deepcopy of "model" not to alter the original model
        m.estimators_ = [model[i] for i in order[: i + 2]]  # select the top "i+2" trees from "model" (variable "i" doesn't get leaked out of list comprehension)
        scores[i] = m.score(x, y)
    k: np.ndarray = np.argsort(scores)[::-1].astype(np.uint16)  # order in descending order based on the performance of top-k decision trees

    mad: float = median_absolute_deviation(scores)
    top_k: np.uint16 = k[0]  # best performing subset of top k-trees (not necessarily all the trees)
    top_score: float = scores[top_k]

    # To improve final model's generalization, we take highest number of trees without significant performance degradation:
    print("Chopping down excess trees...")
    if top_k + 1 != num_trees:  # if we didn't select all trees:
        for n in tqdm(k[1:]):
            if top_score - scores[n] < mad and top_k < n:  # if difference with the highest score is not significant (less than σ):
                top_k = n

    new_model: TreeModel = deepcopy(model)
    new_model.estimators_: list[TreeModel] = model.estimators_[: top_k + 2]
    return convert(model, "pytorch") if hummingnize else model


# @cython.cfunc  # declare as a C-level function; hence only visible internally and it's to be used within current module only
def median_absolute_deviation(arr: list[float]) -> float:  # declaring function's return type only works for C-level functions
    return 1.4826 * np.median(abs(arr - np.median(arr)))
