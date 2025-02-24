import polars as pl
from itertools import combinations
from collections import defaultdict
from tqdm import trange

type ColumnsSet = frozenset[str]


def get_shap_values(df: pl.DataFrame, target: str, model) -> dict[str, float]:
    df = df.drop(target)
    features_set: ColumnsSet = frozenset(df.columns)
    prediction_map: dict[ColumnsSet, float] = {features_set: model.predict(df).mean()}
    shap_map: defaultdict[str, float] = defaultdict(float)

    comb: tuple[str]
    for num_choice in trange(len(features_set), 0, -1):
        for comb in combinations(features_set, num_choice):
            features_subset: ColumnsSet = frozenset(comb)
            df_zero: pl.DataFrame = df.with_columns(pl.lit(0.0).alias(col) for col in features_set - features_subset)
            prediction: float = prediction_map[features_subset]

            if not num_choice == 1:
                for feature in comb:
                    features_subset_minus_feature: ColumnsSet = features_subset - {feature}
                    if features_subset_minus_feature not in prediction_map:
                        prediction_map[features_subset_minus_feature] = model.predict(df_zero.with_columns(pl.lit(0.0).alias(feature))).mean()  # remove "feature"

                    shap_map[feature] += abs(prediction - prediction_map[features_subset_minus_feature])

    total_contribution: float = sum(shap_map.values()) / 100.0
    return {k: round(v / total_contribution, 2) for k, v in sorted(shap_map.items(), key=lambda item: item[1], reverse=True)}
