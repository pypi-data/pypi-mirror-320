# Apple Health Parser

A Python package for parsing and analyzing Apple Health Export data.

## Installation

```bash
pip install parse_apple_health_data
```

## Usage

```python
from parse_apple_health_data import load_health_data

# Create parser instance
parser = load_health_data('export.xml')

# Get data as pandas DataFrames
dataframes = parser.to_dataframes()

# Access specific measurements
steps_df = dataframes['HKQuantityTypeIdentifierStepCount']
sleep_df = dataframes['HKCategoryTypeIdentifierSleepAnalysis']
```

## Features

- Parse Apple Health Export XML files
- Convert health data to pandas DataFrames
- Separate handling for quantity and category measurements
- Preserve all metadata from original export
- Type hints and documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.
