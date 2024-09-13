import os
import logging
import coverage
from datetime import datetime
from utils.input import read_problems
from utils.logging import write_plan_and_tests_qa
from agents.code_architect_agent import architect_code
from agents.test_generator_agent import generate_test_code
import json
from io import StringIO
import subprocess
import runpy
import concurrent.futures
from tools.parse_coverage_html import extract_success_percentage

# Create a timestamped folder for logs
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_folder = os.path.join('logs', f'QAagent-{timestamp}')
os.makedirs(log_folder, exist_ok=True)

# Create a logger
logger = logging.getLogger('QAagentLogger')
logger.setLevel(logging.INFO)

# Create a file handler that logs to the timestamped folder
file_handler = logging.FileHandler(os.path.join(log_folder, 'QAagent.log'))
file_handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

def add_plan(problem_name, pseudocode):
    return f"""{problem_name["prompt"]}

{pseudocode}
"""

def add_canonical_solution(problem_name):
    return f"""{problem_name["prompt"]}
{problem_name["canonical_solution"]}
"""

def calculate_average_coverage(log_folder):
    total_line_coverage = 0
    total_branch_coverage = 0
    count = 0

    for filename in os.listdir(log_folder):
        if filename.startswith('coverage_data_') and filename.endswith('.json'):
            with open(os.path.join(log_folder, filename), 'r') as f:
                data = json.load(f)
                total_line_coverage += data['line_coverage']
                total_branch_coverage += data['branch_coverage']
                count += 1

    if count > 0:
        avg_line_coverage = total_line_coverage / count
        avg_branch_coverage = total_branch_coverage / count
        return avg_line_coverage, avg_branch_coverage
    else:
        return 0, 0

def get_coverage(code_string, test_string, problem_id):
    # Create a temporary module to hold the code

    # write code string to a file in the problem_id folder called temp_problem_id.py
    with open(os.path.join(log_folder, f'problem_{problem_id}', 'temp.py'), 'w') as f2:
        f2.write(code_string)
        f2.write("\n" + test_string)

    # Set up coverage
    cov = coverage.Coverage()

    # Run the tests
    test_result = StringIO()
    try:
        cov.start()
        # Execute temp.py
        runpy.run_path(os.path.join(log_folder, f'problem_{problem_id}', 'temp.py'))

        # Run coverage and execute the file, Generate a coverage report
        subprocess.run(['coverage', 'run', os.path.join(log_folder, f'problem_{problem_id}', 'temp.py')])
        print("All tests passed successfully!")
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
    except Exception as e:
        print(f"An error occurred during testing: {str(e)}")
    finally:
        # Stop coverage and generate report
        cov.stop()
        cov.save()

    # Get coverage report
    report_output = StringIO()
    cov.report(show_missing=True, file=report_output)
    cov.html_report(directory=os.path.join(log_folder, f'problem_{problem_id}'))
    coverage_report = report_output.getvalue()
    return test_result.getvalue(), coverage_report

def qaAgent(problem_name, model_name):
    num_input_tokens = 0
    num_output_tokens = 0
    problem_id = problem_name["task_id"]

    logger.info(f'Starting problem ID {problem_id}')

    # generate pseudocode from problem["prompt"]
    logger.info(f'Generating pseudocode for problem ID {problem_id}')
    plan, plan_input_tokens, plan_output_tokens = architect_code(problem_name,"prompts/v1/code_architect_zero_shot.txt", model_name)
    num_input_tokens += plan_input_tokens
    num_output_tokens += plan_output_tokens
    logger.info(f'Generated plan for problem ID {problem_id}: {plan}')
    logger.info(f'Generated plan input tokens for problem ID {problem_id}: {plan_input_tokens}\nGenerated plan output tokens for problem ID {problem_id}: {plan_output_tokens}')

    # generate a sample canonical solution

    logger.info(f'Generating tests for problem ID {problem_id}')
    try:
        generated_tests, generated_test_input_tokens, generated_test_output_tokens = generate_test_code(add_plan(problem_name, plan), problem_id, "prompts/v1/test_generator_zero_shot.txt", model_name, logger)
    except Exception as e:
        logger.error(f'Error in problem ID {problem_id}: {e}')
        return 0, 0
    num_input_tokens += generated_test_input_tokens
    num_output_tokens += generated_test_output_tokens


    logger.info(f'Generated tests for problem ID {problem_id}: {generated_tests}')
    logger.info(f'Generated test input tokens for problem ID {problem_id}: {generated_test_input_tokens}\nGenerated test output tokens for problem ID {problem_id}: {generated_test_output_tokens}')
    write_plan_and_tests_qa(log_folder, problem_id, plan, generated_tests)

    # check the code coverage of the generated tests
    logger.info(f'Checking code coverage for problem ID {problem_id}')

    test_results, coverage_report = get_coverage(add_canonical_solution(problem_name), generated_tests, problem_id)

    problem_folder = os.path.join(log_folder, f'problem_{problem_id}')


    # Read HTML content from a file or string
    with open(os.path.join(problem_folder, 'class_index.html'), 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Extract and print the success percentage
    coverage_percentage = 0.0
    try:
        success_percentage = extract_success_percentage(html_content)
        print(f'Success Percentage: {success_percentage}')
        coverage_percentage = float(success_percentage.rstrip('%'))
    except ValueError as e:
        print(e)

    print("Test Results:")
    print(test_results)
    print("\nCoverage Report:")
    print(coverage_report)

    with open(os.path.join(problem_folder, 'test_results.txt'), 'w') as f2:
        f2.write(test_results)

    with open(os.path.join(problem_folder, 'coverage_report.txt'), 'w') as f2:
        f2.write(coverage_report)

    # Log the results
    logger.info(f'Finished processing problem ID {problem_id}')
    logger.info(f'Number of input tokens for problem ID {problem_id}: {num_input_tokens}\nNumber of output tokens for problem ID {problem_id}: {num_output_tokens}')
    return coverage_percentage, num_input_tokens, num_output_tokens


def process_problem(problem, model, log_folder):
    try:
        coverage_percentage, cur_num_input_tokens, cur_num_output_tokens = qaAgent(problem, model)
        return problem["task_id"], cur_num_input_tokens, cur_num_output_tokens, coverage_percentage
    except Exception as e:
        logger.error(f'Error in problem ID {problem["task_id"]}: {e}')
        with open(os.path.join(log_folder, 'errors.txt'), 'a') as f:
            f.write(f'Error in problem ID {problem["task_id"]}: {e}\n')
        return problem["task_id"], 0, 0, 0.0  # Return 0 tokens if there's an error

if __name__ == "__main__":
    # Load the model
    # model = "gpt-4o"
    model = "gpt-4"
    # Load the problems
    problems = read_problems("datasets/humaneval/problems.jsonl")

    total_input_tokens = 0
    total_output_tokens = 0
    num_problems_evaluated = 0
    total_coverage_percentage = 0.0

    # Run the QaAgent function on each problem
    start_index = 0
    end_index = 164
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all problems to the executor
        future_to_problem = {executor.submit(process_problem, problems[i], model, log_folder): i for i in
                             range(start_index, end_index)}

        for future in concurrent.futures.as_completed(future_to_problem):
            problem_index = future_to_problem[future]
            try:
                problem_id, cur_num_input_tokens, cur_num_output_tokens, coverage_percentage = future.result()
                total_input_tokens += cur_num_input_tokens
                total_output_tokens += cur_num_output_tokens
                num_problems_evaluated += 1
                total_coverage_percentage += coverage_percentage

                with open(os.path.join(log_folder, 'summary.txt'), 'w') as f:
                    # Log the total number of problems evaluated, total passed, percentage, total input tokens, and total output tokens
                    f.write(f'Total coverage percentage: {total_coverage_percentage / num_problems_evaluated}\n')
                    f.write(f'Total number of problems evaluated: {num_problems_evaluated}\n')
                    f.write(f'Total number of input tokens: {total_input_tokens}\n')
                    f.write(f'Total number of output tokens: {total_output_tokens}\n')

                # Log the results and scores to a detail.txt file for each problem
                with open(os.path.join(log_folder, 'details.txt'), 'a') as f:
                    f.write(f'Problem ID: {problem_id}\n')
                    f.write(f'Coverage Percentage: {coverage_percentage}\n')
                    f.write(f'Number of input tokens: {cur_num_input_tokens}\n')
                    f.write(f'Number of output tokens: {cur_num_output_tokens}\n')
            except Exception as e:
                logger.error(f'Error processing problem at index {problem_index}: {e}')

