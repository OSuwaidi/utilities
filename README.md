# Utilities

A personal collection of Python helpers, technical notes, and editor settings. The
`my_utils` package focuses on Polars-based data preparation and practical machine
learning workflows.

## What is included

- **DataFrames:** missing-data cleanup, numerical scaling, categorical encoding,
  dtype optimization, and reduced row-echelon form.
- **Data cleaning:** consistent snake, kebab, camel, Pascal, or constant-case
  column names, including duplicate and accent handling.
- **Modelling:** feature selection, exogenous ARIMA forecasting, churn estimation,
  tree-ensemble pruning, and experimental SHAP-value calculation.
- **Visualization:** a Panel pane for embedding Lets-Plot charts.
- **Reference material:** notes on Git, Docker, WSL, SSH, ROS, embedded systems,
  Panel, and Python semantics under [`handbook/`](handbook/).
- **Editor settings:** personal PyCharm, VS Code, and Zed configurations under
  [`editor_settings/`](editor_settings/).

## Installation

The current source uses Python 3.12+ syntax. Install the package directly from
GitHub:

```bash
python -m pip install lets-plot hummingbird-ml torch \
  "git+https://github.com/OSuwaidi/utilities.git@main"
```

These additional packages support `LetsPlotPane` and `optimize_trees`; both are
currently loaded by the package's public import but are not declared as core
dependencies.

For local development:

```bash
git clone https://github.com/OSuwaidi/utilities.git
cd utilities
python -m pip install -e .
```

## Quick example

```python
import polars as pl
from my_utils import clean_columns, optimize_dtypes

df = pl.DataFrame({"Customer ID": [1, 2], "Total Spend USD": [12.5, 20.0]})
df.columns = clean_columns(df.columns)
df = optimize_dtypes(df)

print(df.columns)
# ['customer_id', 'total_spend_usd']
```

The package is evolving and several modelling helpers are experimental; review
their docstrings and validate their output before production use.
