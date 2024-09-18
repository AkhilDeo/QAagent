import os
import coverage
import subprocess
from io import StringIO
import runpy

def get_coverage(code_string, test_string, problem_id, log_folder):

    # write code string to a file in the problem_id folder called temp_problem_id.py
    os.makedirs(os.path.join(log_folder, f'problem_{problem_id}', 'first_five_coverage'), exist_ok=True)
    os.makedirs(os.path.join(log_folder, f'problem_{problem_id}', 'total_coverage'), exist_ok=True)

    test_lines = test_string.split('\n')
    filtered_test_lines = [line for line in test_lines if
                           line.strip() and not line.strip().startswith('#') and line.strip().startswith('assert')]

    # Write the combined code and test string to separate files for full and first five tests
    with open(os.path.join(log_folder, f'problem_{problem_id}', 'total_coverage', 'total_coverage.py'), 'w') as f2:
        f2.write(code_string + "\n" + "\n".join(filtered_test_lines))

    # If there are less than five tests, only use the available tests
    if len(filtered_test_lines) < 5:
        first_five_tests = "\n".join(test_lines)
    else:
        first_five_tests = "\n".join(filtered_test_lines[:5])

    with open(os.path.join(log_folder, f'problem_{problem_id}', 'first_five_coverage', 'first_five_coverage.py'), 'w') as f2:
        f2.write(code_string)
        f2.write("\n" + first_five_tests)

    # Set up coverages
    cov_total = coverage.Coverage(concurrency='thread', data_suffix=True)
    try:
        cov_total.start()
        # Run total tests coverage
        runpy.run_path(os.path.join(log_folder, f'problem_{problem_id}', 'total_coverage', 'total_coverage.py'))
        print("All tests passed successfully!")
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
    except Exception as e:
        print(f"An error occurred during testing: {str(e)}")
    finally:
        cov_total.stop()
        cov_total.save()
        # Generate the coverage reports
        report_output_total = StringIO()
        cov_total.report(show_missing=True, file=report_output_total)
        cov_total.html_report(directory=os.path.join(log_folder, f'problem_{problem_id}', 'total_coverage'))

        # Capture the coverage reports
        total_coverage_report = report_output_total.getvalue()
        cov_total.erase()

    # Set up coverages
    cov_five = coverage.Coverage(concurrency='thread', data_suffix=True)
    cov_five.start()
    try:
        # Run total tests coverage
        runpy.run_path(os.path.join(log_folder, f'problem_{problem_id}', 'first_five_coverage', 'first_five_coverage.py'))
        print("All tests passed successfully!")
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
    except Exception as e:
        print(f"An error occurred during testing: {str(e)}")
    finally:
        cov_five.stop()
        cov_five.save()
        # Generate the coverage reports
        report_output_first_five = StringIO()
        cov_five.report(show_missing=True, file=report_output_first_five)
        cov_five.html_report(directory=os.path.join(log_folder, f'problem_{problem_id}', 'first_five_coverage'))

        # Capture the coverage reports
        first_five_coverage_report = report_output_first_five.getvalue()
        cov_five.erase()

    return first_five_coverage_report, total_coverage_report