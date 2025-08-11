import polars as pl
from itertools import combinations
from tqdm import trange
from sklearn.base import BaseEstimator
import pandas as pd
from math import factorial

type FeaturesSet = frozenset[str]


def get_shap_values(df: pl.DataFrame, target: str, model: BaseEstimator) -> pd.DataFrame:
    # TODO: Fix shapley weights
    # TODO: Add local shapley values -> per-row shapley value (each observation/record is a game, each feature is a player)
    # TODO: Allow missing feature treatment to be either all zeros or random values
    df = df.drop(target)
    features_set: FeaturesSet = frozenset(df.columns)
    n = len(features_set)
    prediction_map: dict[FeaturesSet, float] = {features_set: model.predict(df).mean()}
    shap_df: pd.DataFrame = pd.DataFrame({"magnitude": [0.], "direction": [0.]}, index=features_set)

    comb: tuple[str]
    for s in trange(n, 0, -1):
        shap_weight = factorial(s)*factorial(n - s - 1)/factorial(n)
        for comb in combinations(features_set, s):
            coalition: FeaturesSet = frozenset(comb)  # features subset
            df_aug = df.with_columns(pl.lit(0.).alias(col) for col in features_set - coalition)
            base_prediction: float = prediction_map[coalition]

            for feature in comb:
                coalition_minus_feature = coalition - {feature}
                if coalition_minus_feature not in prediction_map:
                    prediction_map[coalition_minus_feature] = model.predict(df_aug.with_columns(pl.lit(0.).alias(feature))).mean()  # remove "feature"

                difference = base_prediction - prediction_map[coalition_minus_feature]
                shap_df.loc[feature, "magnitude"] += abs(difference)
                shap_df.loc[feature, "direction"] += difference

    shap_df["magnitude"] = (100 * shap_df["magnitude"] / shap_df["magnitude"].sum()).round(1)
    shap_df["direction"] = (100 * shap_df["direction"] / shap_df["direction"].abs().sum()).round(1)
    return shap_df.sort_values("magnitude", ascending=False)
