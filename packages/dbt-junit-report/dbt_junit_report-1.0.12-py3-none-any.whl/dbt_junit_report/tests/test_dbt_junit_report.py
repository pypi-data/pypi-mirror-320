import pytest
import json
from pathlib import Path
from dbt_junit_report.dbt_junit_report import convert_run_result_to_junit, InvalidSchemaVersion

def test_valid_schema_version(mocker):
    # Mock json.load to return a dictionary with the expected schema version.
    mocker.patch("json.load", return_value={"metadata": {"dbt_schema_version": "https://schemas.getdbt.com/dbt/run-results/v4.json"}, "results": []})

    # Mock the 'open' function to return a file object.
    mock_file = mocker.mock_open(read_data=json.dumps({"metadata": {"dbt_schema_version": "https://schemas.getdbt.com/dbt/run-results/v4.json"}, "results": []}))
    mocker.patch("builtins.open", mock_file)
    
    mock_response = '''<?xml version="1.0" ?>
<testsuites disabled="0" errors="0" failures="0" tests="0" time="0.0">
\t<testsuite disabled="0" errors="0" failures="0" name="dbt_tests" skipped="0" tests="0" time="0"/>
</testsuites>
'''

    result_file_path = Path("run_results.json")
    junit_file_path = Path("junit_report.xml")
    convert_run_result_to_junit(result_file_path, junit_file_path)
    
    # Assert that the 'open' function was called with the expected arguments.
    mock_file.assert_any_call(junit_file_path, "w")

    # Assert that the file was written to with the expected text.
    mock_file().write.assert_called_once_with(mock_response)

def test_invalid_schema_version(mocker):
    # Mock json.load to return a dictionary with the expected schema version.
    mocker.patch("json.load", return_value={"metadata": {"dbt_schema_version": "invalid_version"}, "results": []})

    # Mock the 'open' function to return a file object.
    mock_file = mocker.mock_open(read_data=json.dumps({"metadata": {"dbt_schema_version": "invalid_version"}, "results": []}))
    mocker.patch("builtins.open", mock_file)
    
    result_file_path = Path("run_results.json")
    junit_file_path = Path("junit_report.xml")
    with pytest.raises(InvalidSchemaVersion):
        convert_run_result_to_junit(result_file_path, junit_file_path)

def test_fail_status(mocker):
    mock_json_data={
    "metadata": {
        "dbt_schema_version": "https://schemas.getdbt.com/dbt/run-results/v4.json"
    },
    "results": [
        {
            "unique_id": "unit_test.project.test1",
            "status": "fail",
            "execution_time": 1.0,
            "compiled_code": "code",
            "message": "failure message"
        }
    ]
}
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_json_data)))
    
    # Mock the 'open' function to return a file object.
    mock_file = mocker.mock_open(read_data=json.dumps(mock_json_data))
    mocker.patch("builtins.open", mock_file)
    
    mock_response = '''<?xml version="1.0" ?>
<testsuites disabled="0" errors="0" failures="1" tests="1" time="1.0">
\t<testsuite disabled="0" errors="0" failures="1" name="dbt_tests" skipped="0" tests="1" time="1.0">
\t\t<testcase name="test1" time="1.000000" classname="unit_test.project" status="fail" class="unit_test" log="code">
\t\t\t<failure type="failure" message="failure message"/>
\t\t</testcase>
\t</testsuite>
</testsuites>
'''

    result_file_path = Path("run_results.json")
    junit_file_path = Path("junit_report.xml")
    convert_run_result_to_junit(result_file_path, junit_file_path)
    
    # Assert that the 'open' function was called with the expected arguments.
    mock_file.assert_any_call(junit_file_path, "w")

    # Assert that the file was written to with the expected text.
    mock_file().write.assert_called_once_with(mock_response)

def test_error_status(mocker):
    mock_json_data = {
        "metadata": {"dbt_schema_version": "https://schemas.getdbt.com/dbt/run-results/v4.json"},
        "results": [{"unique_id": "unit_test.project.test2", "status": "error", "execution_time": 1.0, "compiled_code": "code", "message": "error message"}]
    }
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_json_data)))
    
    # Mock the 'open' function to return a file object.
    mock_file = mocker.mock_open(read_data=json.dumps(mock_json_data))
    mocker.patch("builtins.open", mock_file)
    
    mock_response = '''<?xml version="1.0" ?>
<testsuites disabled="0" errors="1" failures="0" tests="1" time="1.0">
\t<testsuite disabled="0" errors="1" failures="0" name="dbt_tests" skipped="0" tests="1" time="1.0">
\t\t<testcase name="test2" time="1.000000" classname="unit_test.project" status="error" class="unit_test" log="code">
\t\t\t<error type="error" message="error message"/>
\t\t</testcase>
\t</testsuite>
</testsuites>
'''

    result_file_path = Path("run_results.json")
    junit_file_path = Path("junit_report.xml")
    convert_run_result_to_junit(result_file_path, junit_file_path)
    
    # Assert that the 'open' function was called with the expected arguments.
    mock_file.assert_any_call(junit_file_path, "w")

    # Assert that the file was written to with the expected text.
    mock_file().write.assert_called_once_with(mock_response)

def test_skipped_status(mocker):
    mock_json_data = {
        "metadata": {"dbt_schema_version": "https://schemas.getdbt.com/dbt/run-results/v4.json"},
        "results": [{"unique_id": "unit_test.project.test3", "status": "skipped", "execution_time": 1.0, "compiled_code": "code", "message": "skipped message"}]
    }
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_json_data)))

    # Mock the 'open' function to return a file object.
    mock_file = mocker.mock_open(read_data=json.dumps(mock_json_data))
    mocker.patch("builtins.open", mock_file)
    
    mock_response = '''<?xml version="1.0" ?>
<testsuites disabled="0" errors="0" failures="0" tests="1" time="1.0">
\t<testsuite disabled="0" errors="0" failures="0" name="dbt_tests" skipped="1" tests="1" time="1.0">
\t\t<testcase name="test3" time="1.000000" classname="unit_test.project" status="skipped" class="unit_test" log="code">
\t\t\t<skipped type="skipped" message="skipped message"/>
\t\t</testcase>
\t</testsuite>
</testsuites>
'''

    result_file_path = Path("run_results.json")
    junit_file_path = Path("junit_report.xml")
    convert_run_result_to_junit(result_file_path, junit_file_path)
    
    # Assert that the 'open' function was called with the expected arguments.
    mock_file.assert_any_call(junit_file_path, "w")

    # Assert that the file was written to with the expected text.
    mock_file().write.assert_called_once_with(mock_response)