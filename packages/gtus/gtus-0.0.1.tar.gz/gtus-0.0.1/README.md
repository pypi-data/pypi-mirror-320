# GTUS - Google Trends for US States

The **GTUS** package is a Python library designed to collect Google Trends data for specified queries across various U.S. states. It provides functionality to handle multiple queries and states efficiently, while adhering to Google Trends API limitations.

---

## Features

- Collect trends for one or multiple states.
- Batch processing of queries to avoid API limits.
- Adjustable wait time between requests to manage rate limits.
- Export collected data to Excel and JSON formats.
- Access data in a consolidated pandas DataFrame for easy analysis.

---

## Installation

To use the GTUS package, ensure you have the required dependencies installed. You can install them using pip:

```bash
pip install gtus
```

This will automatically install all required dependencies, including `pytrends`, `pandas`, and `aiohttp`.

---

## Getting Started

Here's how to start using GTUS to collect Google Trends data.

### Importing the Package

To use the GTUS package, import it as follows:

```python
from gtus import GTUS
```

### 1. Collect Google Trends Data for US States

#### Collecting for One State

To collect data for a single state, create an instance of the `GTUS` class with the desired query and state:

```python
from gtus import GTUS

queries = ["telemedicine", "remote work"]
states = ["TX"]
gtus = GTUS(queries, states, timeframe="2022-01-01 2023-01-01")

# Collect data
gtus.collect_all_trends()
```

#### Collecting for Multiple States

To collect data for multiple states, simply provide a list of states:

```python
from gtus import GTUS

queries = ["telemedicine", "remote", "football", "dance"]
states = ["CA", "NY", "TX"]
gtus = GTUS(queries, states, timeframe="2020-01-01 2023-01-01")

# Collect data
gtus.collect_all_trends()
```

#### Collecting for All States

If no states are specified, GTUS will automatically collect data for all US states:

```python
queries = ["remote work", "telehealth"]

# Initialize GTUS object
gtus = GTUS(queries=queries, timeframe="2022-01-01 2023-01-01", wait_time=15)
```

### Modifying Wait Time

You can adjust the wait time between requests by specifying the `wait_time` parameter when creating the `GTUS` instance. This is useful for managing API rate limits:

```python
gtus = GTUS(queries, states, wait_time=15)  # Set wait time to 15 seconds
```

### Saving Data

#### Exporting to Excel

To save the collected data to an Excel file, use the `export_to_excel` method:

```python
gtus.export_to_excel("google_trends_data.xlsx")
```

#### Exporting to JSON

To save the collected data to a JSON file, use the `export_to_json` method:

```python
gtus.export_to_json("google_trends_data.json")
```

### Accessing Data in Python

The data collected can be accessed in a consolidated pandas DataFrame. This allows for easy manipulation and analysis:

```python
df = gtus.create_consolidated_dataframe()
print(df.head())
```

### Example Output

The DataFrame will have the following structure:

| date       | State | telemedicine | remote work | football | dance |
|------------|-------|--------------|-------------|----------|-------|
| 2021-12-26 | CA    | 72.0         | 62.0        | 59.0     | 68.0  |
| 2021-12-26 | TX    | 73.0         | 59.0        | 67.0     | 70.0  |

---

## Dependencies

- `pandas`
- `pytrends`
- `aiohttp`
- `openpyxl`

---

## Contributing

Contributions are welcome! Please submit issues or pull requests via [GitHub](https://github.com/leventbulut/gtus).

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

---

Start exploring Google Trends data with GTUS today!
