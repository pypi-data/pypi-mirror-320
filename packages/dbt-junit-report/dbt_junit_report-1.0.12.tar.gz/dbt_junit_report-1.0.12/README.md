# DBT JUnit Report

This repository contains a Python script to convert `dbt` run results into a JUnit report format. This can be useful for integrating `dbt` results with CI/CD pipelines that support JUnit reports.


## Installation

```sh
pip install dbt-junit-report
```


## Usage

To convert a `dbt` run results JSON file to a JUnit report, run the following command:

```sh
dbt_junit_report <path-to-run_results.json> <path-to-output-junit-report.xml>
```

For example:
```sh
dbt_junit_report run_results.json junit_report.xml
```

## Testing

To run the tests, use the following command:

```sh
uv run pytest
```

## Code Overview

### `dbt_junit_report.py`

This script contains the main functionality to convert `dbt` run results to a JUnit report.

- `convert_run_result_to_junit(result_file_path: Path, junit_file_path: Path)`: This function reads the `dbt` run results from the specified JSON file, converts them to JUnit format, and writes the output to the specified XML file.

### `tests/test_dbt_junit_report.py`

This file contains unit tests for the `convert_run_result_to_junit` function using the `pytest` framework.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
