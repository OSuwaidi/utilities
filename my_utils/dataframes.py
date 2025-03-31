from functools import wraps
import polars as pl
import polars.selectors as cs
import numpy as np
from os.path import splitext, abspath
from warnings import warn
from typing import Callable, Self
from sklearn.preprocessing import StandardScaler


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


class NumericalScaler(StandardScaler):
    @staticmethod
    def _check_if_pl_df(method: Callable) -> Callable:
        @wraps(method)
        def boolean_wrapper(self, df: pl.DataFrame) -> pl.DataFrame | None:
            if not isinstance(df, pl.DataFrame):  # better than "assert" because it checks if object is instance of class or subclass of that class as well!
                raise TypeError(f"Expected type {pl.DataFrame}, found {type(df)} instead.")
            return method(self, df)

        return boolean_wrapper

    @_check_if_pl_df
    def fit(self, train_df: pl.DataFrame) -> None:  # new ".fit()" method overrides parent's ".fit()" method
        super().fit(train_df.select(cs.numeric()))  # use the parent class' ".fit()" method

    @_check_if_pl_df
    def transform(self, target_df: pl.DataFrame) -> pl.DataFrame:
        transformed_data: np.ndarray = super().transform(target_df.select(cs.numeric()))
        transformed_data: pl.DataFrame = pl.DataFrame(transformed_data, schema=self.feature_names_in_.tolist()).with_columns(cs.numeric().fill_nan(None))
        return pl.concat((transformed_data, target_df.select(~cs.numeric())), how="horizontal")

    @_check_if_pl_df
    def fit_transform(self, df: pl.DataFrame) -> pl.DataFrame:
        self.fit(df)
        return self.transform(df)


class CategoricalEncoder:
    type ClassMethod = Callable[[Self, pl.DataFrame], pl.DataFrame | None]  # a type alias (cannot be used within "isinstance()")

    # ***note***: it is more performant to scale the numerical features first before using the categorical encoder
    def __init__(self, *, encode_nulls: bool):  # force the argument to be passed as a keyword argument
        self._column_category_map: dict[str, dict[str, float]] = {}
        self.encode_nulls = encode_nulls

    @staticmethod
    def _check_4_str_cols(method: ClassMethod) -> ClassMethod:
        @wraps(method)
        def warn_wrapper(self, df: pl.DataFrame) -> pl.DataFrame | None:
            if not df.select(cs.string()).is_empty():
                warn(
                    f"Dataframe contains column(s): {df.select(cs.string()).columns} of type {str}! String columns will not be included in the encoding. Cast them into type category ({pl.Categorical}) first.",
                    UserWarning,
                )

            return method(self, df)  # returns the *evaluation* of the class's method

        return warn_wrapper

    @_check_4_str_cols
    def fit(self, train_df: pl.DataFrame) -> None:
        for column in (categorical_cols := train_df.select(cs.categorical()).columns):
            if not self.encode_nulls:
                df_worked = train_df.filter(pl.col(column).is_not_null())
            else:
                df_worked = train_df

            df_worked = df_worked.group_by(column).agg(
                (~cs.by_name(categorical_cols) & cs.numeric()).mean()  # do not select the previously categorical columns which got converted into numerical
            )
            categories: list[str] = df_worked[column].to_list()
            values: list[float] = df_worked.drop(column).sum_horizontal().to_list()
            self._column_category_map[column] = {category: value for category, value in zip(categories, values)}

    @_check_4_str_cols
    def transform(self, target_df: pl.DataFrame) -> pl.DataFrame:
        if self._column_category_map:
            for column in self._column_category_map:
                # The condition below, if True, implies the existence of categories in the to-be transformed "df" that didn't exist in the training data
                if unseen_categories := (frozenset(target_df[column].unique()) - frozenset(self._column_category_map[column])):
                    self._column_category_map[column] = self._column_category_map[column] | {unseen_category: 0.0 for unseen_category in unseen_categories}

                target_df = target_df.with_columns(pl.col(column).cast(pl.Utf8).replace(self._column_category_map[column]).cast(pl.Float32))

            return target_df

        else:
            raise RuntimeError(f'This {type(self).__name__} instance is not fitted yet. Call ".fit()" first before transforming.')

    @_check_4_str_cols
    def fit_transform(self, df: pl.DataFrame) -> pl.DataFrame:
        for column in (categorical_cols := df.select(cs.categorical()).columns):
            if not self.encode_nulls:
                df_worked = df.filter(pl.col(column).is_not_null())
            else:
                df_worked = df

            df_worked = df_worked.group_by(column).agg(
                (~cs.by_name(categorical_cols) & cs.numeric()).mean()  # do not select the previously categorical columns which got converted into numerical
            )

            categories: list[str] = df_worked[column].to_list()
            values: list[float] = df_worked.drop(column).sum_horizontal().to_list()
            self._column_category_map[column] = category_map = {category: value for category, value in zip(categories, values)}  # fit phase
            df = df.with_columns(pl.col(column).cast(pl.Utf8).replace(category_map).cast(pl.Float32))  # transform phase (overwrite the column)

        return df


type ColumnNames = tuple[str] | list[str] | str
type ColumnTypes = tuple[object] | list[object] | object


def optimize_dtypes(df: pl.DataFrame, save_parquet_path: str | None = None, *, ignore_columns: ColumnNames = (), ignore_types: ColumnTypes = ()) -> pl.DataFrame:
    optimized_dtypes: dict[str, type] = {}
    df_interest = df.drop(ignore_columns)

    if not isinstance(ignore_types, tuple | list):
        ignore_types = (ignore_types,)

    numeric_ranges = (
        (pl.UInt8, 0, np.iinfo(np.uint8).max),
        (pl.UInt16, 0, np.iinfo(np.uint16).max),
        (pl.UInt32, 0, np.iinfo(np.uint32).max),
        (pl.Int8, np.iinfo(np.int8).min, np.iinfo(np.int8).max),
        (pl.Int16, np.iinfo(np.int16).min, np.iinfo(np.int16).max),
        (pl.Int32, np.iinfo(np.int32).min, np.iinfo(np.int32).max),
        (pl.Float32, np.finfo(np.float32).min, np.finfo(np.float32).max),
    )

    # Process numerical columns:
    if int not in ignore_types:
        for series in pl.concat((df_interest.select(cs.integer().min()), df_interest.select(cs.integer().max()))):  # vertical concatenation (by default)
            min_val, max_val = series

            if min_val >= 0:  # if unsigned integers:
                for dtype_range in numeric_ranges[:3]:
                    if min_val >= dtype_range[1] and max_val <= dtype_range[2]:
                        optimized_dtypes[series.name] = dtype_range[0]
                        break
                else:  # will only be triggered if the "for" loop completed normally, i.e., without encountering a "break"
                    optimized_dtypes[series.name] = pl.UInt64

            else:  # if signed integers:
                for dtype_range in numeric_ranges[3:6]:
                    if min_val >= dtype_range[1] and max_val <= dtype_range[2]:
                        optimized_dtypes[series.name] = dtype_range[0]
                        break
                else:
                    optimized_dtypes[series.name] = pl.Int64

    if float not in ignore_types:
        for series in pl.concat((df_interest.select(cs.float().min()), df_interest.select(cs.float().max()))):  # vertical concatenation (by default)
            min_val, max_val = series[0], series[1]

            if min_val >= numeric_ranges[-1][1] and max_val <= numeric_ranges[-1][2]:
                optimized_dtypes[series.name] = numeric_ranges[-1][0]
            else:
                optimized_dtypes[series.name] = pl.Float64

    # Process string and object columns:
    if str not in ignore_types:
        for series in df_interest.select(cs.string() | cs.object()):
            if series.n_unique() < 0.6 * series.len():  # if 40% or more of the data contains duplicates (entirely repeated cells (entries)):
                optimized_dtypes[series.name] = pl.Categorical

    # "df" below (after assigning) will be different from the original "df" passed into the function; it will be a new, locally defined variable
    # "df" on the left will be different in memory (diff "id()") compared to "df" on the right
    df = df.with_columns(pl.col(column).cast(dtype) for column, dtype in optimized_dtypes.items())  # overwrite the columns

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
