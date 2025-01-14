# Solvis Evaluations API

This is a package for requesting and processing data from Solvis's evaluations API.
The package is designed to handle request evaluations and efficiently transforming them into a tabular format (pandas dataframe) suitable for analysis.


## Features

- Request data from the following endpoints:
  - Evaluations
- Converts csv data into a flat pandas dataframe.
- Robust handling of unexpected or malformed data.
- Logging for process tracking and debugging.


## Installation

Install the package via pip (or your favorite package manager):

```bash
pip install solvis-evaluations-api
```


## Usage

### Importing the Module

```python
from solvis_evaluations_api import GetEvaluations
```

### Example

```python
# Initialize modules
api = GetEvaluations()

# Request API
evaluations = api.get_evaluations(
    user='',
    password='',
    survey_id='',
    start_datetime='01/01/2024',
    end_datetime='01/01/2024',
)

# Print output
print(df)
```


## Dependencies

- Python 3.12+
- Pandas
- Requests


## Contact

For questions or feedback, feel free to reach out:

- Author: Paulo Victor
- Email: paulo.barbosa@solvis.com.br