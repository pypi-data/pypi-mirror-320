#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from junit_xml import TestSuite, TestCase, to_xml_report_file

class InvalidSchemaVersion(Exception):
    pass


def convert_run_result_to_junit(result_file_path: Path, junit_file_path: Path):
    with open(result_file_path) as f:
        run_results = json.load(f)

    schema_version = run_results["metadata"]["dbt_schema_version"]

    if schema_version not in [
            "https://schemas.getdbt.com/dbt/run-results/v4.json",
            "https://schemas.getdbt.com/dbt/run-results/v5.json",
            "https://schemas.getdbt.com/dbt/run-results/v6.json"]:
        raise InvalidSchemaVersion(
                f"the schema version { schema_version } is not supported, only (v4-v6) are.",
            )

    test_cases = []
    for result in run_results['results']:
        class_name = ".".join(result['unique_id'].split(".")[:-1])
        test_name = result['unique_id'].split(".")[-1]
        category = result["unique_id"].split(".")[0]
        status = result['status']
        execution_time = result['execution_time']
        compiled_code = result.get('compiled_code','')
        message = result.get('message', '')

        test_case = TestCase(classname=class_name, name=test_name, elapsed_sec=execution_time, status=status, log=compiled_code, category=category)

        if status in ['fail','warn']:
            test_case.add_failure_info(message=message)
            
        if status in ['error','runtime error']:
            test_case.add_error_info(message=message)            
            
        if status == 'skipped':
            test_case.add_skipped_info(message=message)
    
        test_cases.append(test_case)

   
    test_suite = TestSuite("dbt_tests", test_cases)

    with open(junit_file_path, 'w') as f:
        to_xml_report_file(f, [test_suite])

    print(f'JUnit report generated at {junit_file_path} from dbt {result_file_path} file')


def main():
    parser = argparse.ArgumentParser(description="Convert dbt run_results.json to junit report")
    parser.add_argument("result_file_path", type=Path, help="Path to run_results.json")
    parser.add_argument("junit_file_path", type=Path, help="Output path filename for Junit report")
    args = parser.parse_args()

    convert_run_result_to_junit(args.result_file_path, args.junit_file_path)


if __name__ == "__main__":
    main()
