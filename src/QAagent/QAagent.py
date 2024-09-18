import os
import logging
from datetime import datetime
from utils.input import read_problems
from utils.logging import write_plan_and_tests_qa
from agents.code_architect_agent import architect_code
from agents.test_generator_agent import generate_test_code
import concurrent.futures
from tools.parse_coverage_html import extract_success_percentage
from utils.coverage import get_coverage
from utils.accuracy import get_accuracy
import argparse

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

def qaAgent(problem_name, dataset, model_name, code_architect_prompt, test_generator_prompt):
    num_input_tokens = 0
    num_output_tokens = 0
    problem_id = problem_name["task_id"]

    logger.info(f'Starting problem ID {problem_id}')

    # generate pseudocode from problem["prompt"]
    logger.info(f'Generating pseudocode for problem ID {problem_id}')
    plan, plan_input_tokens, plan_output_tokens = architect_code(problem_name,code_architect_prompt, model_name)
    num_input_tokens += plan_input_tokens
    num_output_tokens += plan_output_tokens
    logger.info(f'Generated plan for problem ID {problem_id}: {plan}')
    logger.info(f'Generated plan input tokens for problem ID {problem_id}: {plan_input_tokens}\nGenerated plan output tokens for problem ID {problem_id}: {plan_output_tokens}')

    # generate a sample canonical solution

    logger.info(f'Generating tests for problem ID {problem_id}')
    try:
        generated_tests, generated_test_input_tokens, generated_test_output_tokens, _ = generate_test_code(add_plan(problem_name, plan), problem_id, test_generator_prompt, model_name, logger)
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

    first_five_coverage_report, total_coverage_report = get_coverage(add_canonical_solution(problem_name) if dataset == "humaneval" else problem_name["canonical_solution"], generated_tests, problem_id, log_folder)

    problem_folder = os.path.join(log_folder, f'problem_{problem_id}')

    # Calculate generated tests accuracy on the canonical solution. # passes / total tests
    accuracy, test_results = get_accuracy(add_canonical_solution(problem_name) if args.dataset == "humaneval" else problem_name["canonical_solution"], generated_tests, problem_folder, problem_id)

    with open(os.path.join(problem_folder, 'test_results_accuracy.txt'), 'w') as f2:
        f2.write(test_results)

    with open(os.path.join(problem_folder, 'first_five_coverage', 'function_index.html'), 'r', encoding='utf-8') as file:
        html_content_first_five = file.read()

    with open(os.path.join(problem_folder, 'total_coverage', 'function_index.html'), 'r', encoding='utf-8') as file:
        html_content_total = file.read()

    # Extract and print the success percentage
    current_first_five_coverage_percentage = 0.0
    current_total_coverage_percentage = 0.0
    try:
        first_five_success_percentage = extract_success_percentage(html_content_first_five, problem_name["entry_point"])
        print(f'First Five Success Percentage: {first_five_success_percentage}')
        current_first_five_coverage_percentage = float(first_five_success_percentage.rstrip('%'))
        total_success_percentage = extract_success_percentage(html_content_total, problem_name["entry_point"])
        print(f'Total Success Percentage: {total_success_percentage}')
        current_total_coverage_percentage = float(total_success_percentage.rstrip('%'))
    except ValueError as e:
        print(e)

    print("Test Results:")
    print(test_results)
    print("\nFirst Five Coverage Report:")
    print(first_five_coverage_report)
    print("\nTotal Five Coverage Report:")
    print(total_coverage_report)

    with open(os.path.join(problem_folder, 'first_five_coverage_report.txt'), 'w') as f2:
        f2.write(first_five_coverage_report)

    with open(os.path.join(problem_folder, 'total_coverage_report.txt'), 'w') as f2:
        f2.write(total_coverage_report)

    # Log the results
    logger.info(f'Finished processing problem ID {problem_id}')
    logger.info(f'Number of input tokens for problem ID {problem_id}: {num_input_tokens}\nNumber of output tokens for problem ID {problem_id}: {num_output_tokens}')
    return current_first_five_coverage_percentage, current_total_coverage_percentage, accuracy, num_input_tokens, num_output_tokens


def process_problem(problem, model, dataset, log_folder, code_architect_prompt, test_generator_prompt):
    try:
        curr_first_five_coverage_percentage, curr_total_coverage_percentage, accuracy_percentage, curr_num_input_tokens, curr_num_output_tokens = qaAgent(problem, dataset, model, code_architect_prompt, test_generator_prompt)
        return problem["task_id"], curr_num_input_tokens, curr_num_output_tokens, curr_first_five_coverage_percentage, curr_total_coverage_percentage, accuracy_percentage
    except Exception as e:
        logger.error(f'Error in problem ID {problem["task_id"]}: {e}')
        with open(os.path.join(log_folder, 'errors.txt'), 'a') as f:
            f.write(f'Error in problem ID {problem["task_id"]}: {e}\n')
        return problem["task_id"], 0, 0, 0.0, 0.0, 0.0  # Return 0 tokens if there's an error

def parse_args():
    parser = argparse.ArgumentParser(description="Specify dataset and model.")

    parser.add_argument(
        "--dataset",
        choices=["humaneval", "mbpp"],
        default="mbpp",
        help="Choose the dataset to use (humaneval or mbpp)."
    )

    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="Specify the model to use."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Load the model
    model = args.model
    print(f"Using model: {model}")

    # Load the problems based on dataset choice
    dataset_map = {
        "humaneval": "datasets/humaneval/problems.jsonl",
        "mbpp": "datasets/mbpp/problems.jsonl"
    }

    # Map dataset to its respective prompt paths
    prompt_paths = {
        "humaneval": {
            "code_architect": "prompts/v1/code_architect_humaneval_prompt.txt",
            "test_generator": "prompts/v1/test_generator_humaneval_prompt.txt"
        },
        "mbpp": {
            "code_architect": "prompts/v1/code_architect_mbpp_prompt.txt",
            "test_generator": "prompts/v1/test_generator_mbpp_prompt.txt"
        }
    }

    # Select the appropriate prompt files based on the dataset
    code_architect_prompt = prompt_paths[args.dataset]["code_architect"]
    test_generator_prompt = prompt_paths[args.dataset]["test_generator"]

    # Load the problems
    problems = read_problems(dataset_map[args.dataset])
    print(f"Loaded problems from: {dataset_map[args.dataset]}")

    total_input_tokens = 0
    total_output_tokens = 0
    num_problems_evaluated = 0
    total_first_five_coverage_percentage = 0.0
    total_coverage_percentage = 0.0
    total_accuracy_percentage = 0.0

    # Run the QaAgent function on each problem
    start_index = 98
    end_index = 164 if args.dataset == "humaneval" else 500
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit all problems to the executor
        future_to_problem = {executor.submit(process_problem, problems[i], model, args.dataset, log_folder, code_architect_prompt, test_generator_prompt): i for i in
                             range(start_index, end_index)}

        for future in concurrent.futures.as_completed(future_to_problem):
            problem_index = future_to_problem[future]
            try:
                problem_id, cur_num_input_tokens, cur_num_output_tokens, cur_first_five_coverage_percentage, cur_total_coverage_percentage, cur_accuracy_percentage = future.result()
                total_input_tokens += cur_num_input_tokens
                total_output_tokens += cur_num_output_tokens
                num_problems_evaluated += 1
                total_first_five_coverage_percentage += cur_first_five_coverage_percentage
                total_coverage_percentage += cur_total_coverage_percentage
                total_accuracy_percentage += cur_accuracy_percentage

                with open(os.path.join(log_folder, 'summary.txt'), 'w') as f:
                    # Log the total number of problems evaluated, total passed, percentage, total input tokens, and total output tokens
                    f.write(f'Total accuracy percentage: {total_accuracy_percentage / num_problems_evaluated}\n')
                    f.write(f'Total first five coverage percentage: {total_first_five_coverage_percentage / num_problems_evaluated}\n')
                    f.write(f'Total coverage percentage: {total_coverage_percentage / num_problems_evaluated}\n')
                    f.write(f'Total number of problems evaluated: {num_problems_evaluated}\n')
                    f.write(f'Total number of input tokens: {total_input_tokens}\n')
                    f.write(f'Total number of output tokens: {total_output_tokens}\n')

                # Log the results and scores to a detail.txt file for each problem
                with open(os.path.join(log_folder, 'details.txt'), 'a') as f:
                    f.write(f'Problem ID: {problem_id}\n')
                    f.write(f'Accuracy Percentage: {cur_accuracy_percentage}\n')
                    f.write(f'First Five Coverage Percentage: {cur_first_five_coverage_percentage}\n')
                    f.write(f'Coverage Percentage: {cur_total_coverage_percentage}\n')
                    f.write(f'Number of input tokens: {cur_num_input_tokens}\n')
                    f.write(f'Number of output tokens: {cur_num_output_tokens}\n')
            except Exception as e:
                logger.error(f'Error processing problem at index {problem_index}: {e}')

