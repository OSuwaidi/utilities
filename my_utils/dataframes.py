from functools import wraps
import polars as pl
import polars.selectors as cs
import numpy as np
from os.path import splitext, abspath
from warnings import warn
from typing import Callable, Self, Literal, Iterable
from sklearn.preprocessing import StandardScaler, RobustScaler


def smart_drop(df: pl.DataFrame) -> pl.DataFrame:
    height = df.height
    null_cols = sorted((col_nulls.item(), col_nulls.name) for col_nulls in df.null_count() if col_nulls.item() != 0)
    for null_count, column_name in null_cols:
        # Every cell (entry) in the dataframe counts as a single unit of information
        info_lost_col_drop = height - null_count
        df_missing = df.filter(pl.col(column_name).is_null())
        info_lost_row_drop = df_missing.height * df_missing.width - df_missing.null_count().sum_horizontal().item()
        if info_lost_col_drop <= info_lost_row_drop:
            df = df.drop(column_name)
        else:
            df = df.filter(~pl.col(column_name).is_null())
    return df


class NumericalScaler:
    # TODO: enable inverse transformation
    def __init__(self, *, kind: Literal["robust", "standard"]):
        if kind not in {"robust", "standard"}:
            raise ValueError("kind must be 'robust' or 'standard'")

        self.ignore_cols = ()
        self.scaler = RobustScaler() if kind == "robust" else StandardScaler()

    def __getattr__(self, name: str):
        # Only called if attribute "name" isn't found on self (the instance)
        return getattr(self.scaler, name)

    def __dir__(self):
        # include class' own attributes + all of scaler’s to give attrs visibility for IDE support (tab-completion)
        return list(super().__dir__()) + [a for a in dir(self.scaler) if not a.startswith("_")]

    @staticmethod
    def _check_if_pl_df(method: Callable) -> Callable:
        @wraps(method)
        def check_wrapper(self, df: pl.DataFrame, *args, **kwargs) -> pl.DataFrame | None:
            if not isinstance(df, pl.DataFrame):  # better than "assert" because it checks if object is instance of class or subclass of that class as well!
                raise TypeError(f"Expected type {pl.DataFrame}, found {type(df)} instead.")
            return method(self, df, *args, **kwargs)

        return check_wrapper

    @_check_if_pl_df
    def fit(self, train_df: pl.DataFrame, ignore_cols: Iterable[str] | str = ()) -> None:  # new ".fit()" method overrides parent's ".fit()" method
        self.ignore_cols = ignore_cols
        self.scaler.fit(
            train_df.select(cs.numeric()).drop(ignore_cols)
        )

    @_check_if_pl_df
    def transform(self, target_df: pl.DataFrame) -> pl.DataFrame:
        transformed_data: np.ndarray = self.scaler.transform(
            target_df.select(cs.numeric()).drop(self.ignore_cols)
        )
        transformed_data: pl.DataFrame = (pl.DataFrame(transformed_data, schema=self.feature_names_in_.tolist())
                                          .with_columns(cs.numeric().fill_nan(None))
                                          )
        return pl.concat(
            (
                transformed_data, target_df.select(~cs.numeric(), pl.col(self.ignore_cols or ()))
            ), how="horizontal")

    @_check_if_pl_df
    def fit_transform(self, df: pl.DataFrame, ignore_cols: Iterable[str] | str = ()) -> pl.DataFrame:
        self.fit(df, ignore_cols)
        return self.transform(df)


class CategoricalEncoder:
    # TODO: enable inverse transformation (number -> category)
    # TODO: Fix when using FIT_TRANSFORM AGAIN
    # TODO: DATA NEEDS TO BE ON SAME SCALE BEFORE BEING USED FOR ENCODING
    type ClassMethod = Callable[[Self, pl.DataFrame, ...], pl.DataFrame | None]  # a type alias (cannot be used within "isinstance()")

    # ***note***: it is more performant to scale the numerical features first before using the categorical encoder
    def __init__(self, *, encode_nulls: bool):  # force the argument to be passed as a keyword argument
        self._column_category_map: dict[str, dict[str, float]] = {}
        self.encode_nulls = encode_nulls

    @staticmethod
    def _check_4_str_cols(method: ClassMethod) -> ClassMethod:
        @wraps(method)
        def warn_wrapper(self, df: pl.DataFrame, *args, **kwargs) -> pl.DataFrame | None:
            if not df.select(cs.string()).is_empty():
                warn(
                    f"""Dataframe contains column(s): {df.select(cs.string()).columns} of type string!
                    String columns will be included in the encoding by being cast into type category ({pl.Categorical}) first.""",
                    UserWarning,
                )

            return method(self, df, *args, **kwargs)  # returns the *evaluation* of the class's method

        return warn_wrapper

    @_check_4_str_cols
    def fit(self, train_df: pl.DataFrame) -> None:
        if train_df.select(cs.numeric()).is_empty():
            raise ValueError("DataFrame contains no numeric columns to fit the scaler.")

        train_df = train_df.with_columns(cs.string().cast(pl.Categorical))
        for column in train_df.select(cs.categorical()).columns:
            df_worked = train_df.drop_nulls(column) if not self.encode_nulls else train_df
            df_worked = df_worked.group_by(column).agg(cs.numeric().mean())
            categories: list[str] = df_worked[column].to_list()
            values: list[float] = df_worked.drop(column).sum_horizontal().to_list()
            self._column_category_map[column] = {category: value for category, value in zip(categories, values)}

    @_check_4_str_cols
    def transform(self, target_df: pl.DataFrame) -> pl.DataFrame:
        if not self._column_category_map:
            raise RuntimeError(f'This {type(self).__name__} instance is not fitted yet. Call ".fit()" first before transforming.')

        for column in self._column_category_map:
            # The condition below, if True, implies the existence of categories in the to-be transformed "df" that didn't exist in the training data
            seen_categories = frozenset(self._column_category_map[column])
            if unseen_categories := [new_cat for new_cat in target_df[column].unique() if new_cat not in seen_categories]:
                self._column_category_map[column] |= {unseen_category: 0.0 for unseen_category in unseen_categories}

        replace_expr = (pl.col(column).cast(pl.String).replace(category_map).cast(pl.Float32) for column, category_map in self._column_category_map.items())
        return target_df.with_columns(replace_expr)

    @_check_4_str_cols
    def fit_transform(self, df: pl.DataFrame) -> pl.DataFrame:
        self.fit(df)
        return self.transform(df)


type ColumnNames = tuple[str] | list[str] | str
type ColumnTypes = tuple[object] | list[object] | object


def optimize_dtypes(df: pl.DataFrame, save_parquet_path: str | None = None, *, ignore_columns: ColumnNames = (), ignore_types: ColumnTypes = ()) -> pl.DataFrame:
    optimized_dtypes: dict[str, pl.DataTypeClass] = {}
    df_interest = df.drop(ignore_columns)

    if not isinstance(ignore_types, tuple | list):
        ignore_types = (ignore_types,)

    type_min: Callable[[pl.DataTypeClass], int] = lambda pl_type: pl.select(pl_type.min()).item()
    type_max: Callable[[pl.DataTypeClass], int] = lambda pl_type: pl.select(pl_type.max()).item()

    u_ints = (pl.UInt8, pl.UInt16, pl.UInt32)
    ints = (pl.Int8, pl.Int16, pl.Int32)

    # Process numerical columns:
    if int not in ignore_types:
        for series in df_interest.select(pl.struct(pl.min(col), pl.max(col).alias('max')) for col in df_interest.select(cs.numeric()).columns):
            # "series" here is single entry (one row) "pl.Series" containing a dictionary, where keys are column names and values are the corresponding aggregates
            min_val, max_val = series[0].values()  # access the first entry (row) of the series, then get the dictionary values

            if min_val >= 0:  # if unsigned integers:
                for uint_type in u_ints:
                    if max_val <= type_max(uint_type):
                        optimized_dtypes[series.name] = uint_type
                        break
                else:  # will only be triggered if the "for" loop completed normally, i.e., without encountering a "break"
                    optimized_dtypes[series.name] = pl.UInt64

            else:  # if signed integers:
                for int_type in ints:
                    if min_val >= type_min(int_type) and max_val <= type_max(int_type):
                        optimized_dtypes[series.name] = int_type
                        break
                else:
                    optimized_dtypes[series.name] = pl.Int64

    if float not in ignore_types:
        for series in df_interest.select(pl.struct(pl.min(col), pl.max(col).alias('max')) for col in df_interest.select(cs.float() | cs.decimal()).columns):
            min_val, max_val = series[0].values()

            if min_val >= np.finfo(np.float32).min.item() and max_val <= np.finfo(np.float32).max.item():
                optimized_dtypes[series.name] = pl.Float32
            else:
                optimized_dtypes[series.name] = pl.Float64

    # Process string and object columns:
    if str not in ignore_types:
        for series in df_interest.select(cs.string() | cs.object()):
            if series.n_unique() / series.len() < 0.6:  # if 40% or more of the data contains duplicates (entirely repeated cells (entries)):
                optimized_dtypes[series.name] = pl.Categorical

    # "df" below (after assignment) will be different from the original "df" passed into the function; it will be a new copy of locally defined variable
    # "df" on the left will be different in memory "id()" compared to "df" on the right
    df = df.cast(optimized_dtypes)  # overwrite the columns

    if save_parquet_path:
        file_path, ext = splitext(save_parquet_path)
        try:
            df.write_parquet(file_path + ".parquet")
        except Exception as e:
            raise Exception(f"Failed to save parquet file in path: {abspath(file_path)}, due to {str(e)}.")
        else:  # will execute only if "try" block succeeds (no exception raised)
            print(f"Successfully saved parquet file in: {abspath(file_path)}.parquet")

    return df


def rref(A: np.ndarray) -> np.ndarray:
    A = A.astype(np.float64)
    rows, cols = A.shape

    for idx in range(min(rows, cols)):
        # Find the maximum pivot row for this column (improves numerical stability and avoids a zero-valued pivot)
        pivot_idx = np.abs(A[idx:, idx]).argmax() + idx
        if A[pivot_idx, idx] == 0:
            continue

        # Swap rows to move pivot row to the top
        A[[idx, pivot_idx]] = A[[pivot_idx, idx]]

        # Normalize pivot row for this column
        A[idx] /= A[idx, idx]

        # Eliminate all other entries (rows) in this column
        for i in range(rows):
            if i != idx:
                A[i] -= A[i, idx] * A[idx]

    return A
