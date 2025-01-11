# Macroecon-Tools
A open-source set of tools to assist with macroeconomic work. Extrends the pandas series class into an adjusted timeseries class along with other functionality.

# Timeseries and TimeseriesTable Package

This Python package provides two custom classes, `Timeseries` and `TimeseriesTable`, for working with time series data and collections of time series. It builds on `pandas` and `numpy` to offer additional metadata and advanced operations tailored for macroeconomic analysis of time series

---

## Features

### Timeseries Class
The `Timeseries` class extends `pandas.Series` and adds the following functionality:
- **Metadata Tracking**: Includes attributes like `name`, `source_freq`, `data_source`, and `transformations`. Automatically appends the applied functions to `transformations`.

- **Transformation Methods**:
  - `logdiff`: Compute the log difference of the series.
  - `diff`: Compute the difference over a specified lag.
  - `log` and `log100`: Apply logarithmic transformations. (Note: log100 multiplies the log by 100).
- **Aggregation**:
  - Aggregate data into different timeframes (e.g., monthly, quarterly) using methods like `sum`, `mean`, and `lastvalue`.
- **Filtering**:
  - Apply linear or Hamilton filtering methods.
- **Truncation**:
  - Restrict the series to a specific time range.
- **Persistence**:
  - Save and load timeseries objects using pickle.
- **Custom Representation**:
  - Enhanced string representations for easier inspection.

### TimeseriesTable Class
The `TimeseriesTable` class manages collections of `Timeseries` objects:
- Maintains both a dictionary-like structure and a `pandas.DataFrame` representation.
- Supports operations like truncation, dropping missing values, and correlation computation.
- Facilitates saving and loading the entire TimeseriesTable.

-**to_latex**:
  - Convert the table to a LaTeX table for easy inclusion in reports.
-**trunc**:
  - Truncate the table to a specific time range.
-**corr**:
  - Compute the correlation matrix of the table.
-**dropna**:
  - Drop missing values from the table.

---

## Usage

### Timeseries Class
```python
import pandas as pd
from timeseries import Timeseries

# Create a sample Timeseries
data = pd.Series([1 + 0.3 * i for i in range(10)], index=pd.date_range('2024-01-01', periods=10))
ts = Timeseries(data, name="Sample Data", source_freq="daily", data_source="Generated")

# Apply transformations
log_diff = ts.logdiff(1)
truncated = ts.trunc('2024-01-01', '2024-01-04')
```

### TimeseriesTable Class
```python
import pandas as pd
from timeseries import TimeseriesTable, Timeseries

# Create a sample TimeseriesTable
table_data = {
    "series1": Timeseries(pd.Series([1.1, 1.2, 1.3], index=pd.date_range('2024-01-01', periods=3))),
    "series2": Timeseries(pd.Series([2.1, 2.2, 2.3], index=pd.date_range('2024-01-01', periods=3))),
}
table = TimeseriesTable(table_data)

# Perform operations
correlation_matrix = table.corr()
truncated_table = table.trunc('2024-01-01', '2024-01-02')
```
