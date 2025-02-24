import polars as pl
import numpy as np
from sklearn.feature_selection import RFECV
from sklearn.inspection import permutation_importance
from sklearn.ensemble import ExtraTreesRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from scipy.stats import gamma
from datetime import date
from tqdm import trange
from rich import print
import warnings


def select_important_features(
    x: pl.DataFrame,
    y: pl.Series,
    num_features_to_select: int = 3,
    cv=5,
    random_state: int = np.random.randint(100),
    n_estimators: int = 50,
    return_importance: bool = True,
    n_repeats: int = 10,
):
    assert isinstance(x, pl.DataFrame), f"Expected a Polars dataframe, got {type(x)} instead."

    model = ExtraTreesRegressor(n_estimators=n_estimators, random_state=random_state)
    model = RFECV(model, cv=cv, min_features_to_select=num_features_to_select)
    model.fit(x.to_numpy(), y)

    if return_importance:
        unimportant_features: list[str] = [feature for feature, important in zip(x.columns, model.support_) if not important]
        x = x.with_columns(pl.lit(0.0).alias(unimportant_feature) for unimportant_feature in unimportant_features)

        importance: np.ndarray = permutation_importance(model, x, y, n_repeats=n_repeats, n_jobs=-1, random_state=random_state).importances_mean
        importance /= importance.sum() * 0.01  # normalize importance
        orders = np.argsort(importance)[::-1][:num_features_to_select]

        return {x.columns[i]: importance[i] for i in orders}

    return [feature for feature, important in zip(x.columns, model.support_) if important]


warnings.filterwarnings("ignore", category=ConvergenceWarning)


class ExogArima:
    def __init__(self, x: pl.DataFrame, y: pl.Series, future_steps: int):
        self.x = x.to_numpy()  # exogenous variables' data
        self.y = y.to_numpy()  # variable to be forecasted given forecasted exogenous variables
        self.future_steps = future_steps
        self.fc_exog: np.ndarray = np.empty((future_steps, self.x.shape[1]))  # initialize empty forecasted exogenous data
        self.residuals: list[float] = [0.0] * self.x.shape[1]  # residuals of all forecasted variables

    def generate_forecasted_exog(self, order: tuple = (1, 0, 1), seasonal_order: tuple = (1, 0, 1, 12), print_residuals: bool = False) -> None:
        model = ARIMA(self.x[:, 0], order=order, seasonal_order=seasonal_order).fit()  # fit against the first variable alone
        # Populate the initial forecasted exogenous variable, without using other exogenous variables (must start somewhere)
        self.fc_exog[:, 0] = model.forecast(steps=self.future_steps, dynamic=True)
        self.residuals[0] = np.linalg.norm(model.resid)

        for i in trange(1, self.fc_exog.shape[1]):
            model = ARIMA(self.x[:, i], exog=self.x[:, :i], order=order, seasonal_order=seasonal_order).fit()  # fit against the ith variable and "i" exog variables
            # Populate ith forecasted exogenous variable using "i" previously forecasted exogenous variables (populate sequentially):
            self.fc_exog[:, i] = model.forecast(steps=self.future_steps, exog=self.fc_exog[:, :i], dynamic=True)
            self.residuals[i] = np.linalg.norm(model.resid)  # measures how well the forecasted data compares to the observed data

        if print_residuals:
            print(f"Average residual of exogenous variables: {np.mean(self.residuals):.2f}")

    def forecast_target(self, order: tuple = (1, 0, 1), seasonal_order: tuple = (1, 0, 1, 12), print_residuals: bool = False) -> np.ndarray:
        model = ARIMA(self.y, exog=self.x, order=order, seasonal_order=seasonal_order).fit()
        future_forecast = model.forecast(steps=self.future_steps, exog=self.fc_exog, dynamic=True)

        if print_residuals:
            print(f"Average residual of target variable: {np.linalg.norm(model.resid):.2f}")

        return future_forecast


def predict_churn(df: pl.DataFrame, date_column: str, sort: bool = False) -> float:
    assert isinstance(df[date_column].dtype, (pl.Date, pl.Datetime)), f"Expected type {pl.Date, pl.Datetime}, got {df[date_column].dtype} instead."

    if isinstance(df[date_column].dtype, pl.Datetime):
        df = df.with_columns(pl.col(date_column).cast(pl.Date))

    if sort:  # the dataframe's date column MUST be sorted in ascending order!
        last_date = df[date_column].sort()[-1]
    else:
        last_date = df[date_column][-1]

    days_since_last_event: int = (date.today() - last_date).days
    days_diff: pl.Series = df[date_column].diff()[1:].dt.total_days()
    days_diff = days_diff.filter(days_diff != 0)  # remove transactions that occurred on the same day
    if days_diff.is_empty():  # if a single transaction:
        return days_since_last_event / (1 + days_since_last_event)
    if days_diff.std() == 0 or (days_diff.len() == 1):  # if all transactions are on the same date or single difference info:
        return days_since_last_event / (days_diff[0] + days_since_last_event)
    params = gamma.fit(days_diff)  # returns 3 distribution parameters: (shape, location, scale)
    return gamma.cdf(days_since_last_event, *params)  # computes the integral from 0 to "x"
