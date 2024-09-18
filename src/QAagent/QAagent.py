import os
import concurrent.futures
from utils.utils import read_problems, add_plan, add_canonical_solution, parse_args, update_total_stats
from utils.logging import write_plan_and_tests_qa, create_log_folder, setup_logger, log_results, write_summary, write_details
from agents.code_architect_agent import architect_code
from agents.test_generator_agent import generate_test_code
from utils.coverage import get_coverage, extract_coverage_percentages
from utils.accuracy import get_accuracy


def generate_plan(problem_name, code_architect_prompt, model_name, logger):
    logger.info(f'Generating pseudocode for problem ID {problem_name["task_id"]}')
    plan, plan_input_tokens, plan_output_tokens = architect_code(problem_name, code_architect_prompt, model_name)
    logger.info(f'Generated plan: {plan}\nInput tokens: {plan_input_tokens}, Output tokens: {plan_output_tokens}')
    return plan, plan_input_tokens, plan_output_tokens

def generate_tests(problem_name, plan, test_generator_prompt, model_name, logger):
    logger.info(f'Generating tests for problem ID {problem_name["task_id"]}')
    try:
        tests, test_input_tokens, test_output_tokens, _ = generate_test_code(
            add_plan(problem_name, plan), problem_name["task_id"], test_generator_prompt, model_name, logger
        )
        logger.info(f'Generated tests: {tests}\nInput tokens: {test_input_tokens}, Output tokens: {test_output_tokens}')
        return tests, test_input_tokens, test_output_tokens
    except Exception as e:
        logger.error(f'Error generating tests: {e}')
        raise

def qaAgent(problem_name, dataset, model_name, code_architect_prompt, test_generator_prompt):
    num_input_tokens = 0
    num_output_tokens = 0
    problem_id = problem_name["task_id"]
    logger.info(f'Starting problem ID {problem_id}')

    # generate natural language pseudocode from problem["prompt"]
    plan, plan_input_tokens, plan_output_tokens = generate_plan(problem_name, code_architect_prompt, model_name, logger)
    num_input_tokens += plan_input_tokens
    num_output_tokens += plan_output_tokens

    # generate tests
    logger.info(f'Generating tests for problem ID {problem_id}')
    try:
        generated_tests, test_input_tokens, test_output_tokens = generate_tests(problem_name, plan, test_generator_prompt, model_name, logger)
        num_input_tokens += test_input_tokens
        num_output_tokens += test_output_tokens
    except Exception:
        return 0, 0, 0, 0, 0

    # log plan/pseudocode and tests
    write_plan_and_tests_qa(log_folder, problem_id, plan, generated_tests)

    # check the code coverage of the generated tests
    logger.info(f'Checking code coverage for problem ID {problem_id}')

    # get coverage reports
    first_five_coverage_report, total_coverage_report = get_coverage(add_canonical_solution(problem_name) if dataset == "humaneval" else problem_name["canonical_solution"], generated_tests, problem_id, log_folder)

    # Calculate generated tests accuracy on the canonical solution. # passes / total tests
    problem_folder = os.path.join(log_folder, f'problem_{problem_id}')
    accuracy, test_results = get_accuracy(add_canonical_solution(problem_name) if args.dataset == "humaneval" else problem_name["canonical_solution"], generated_tests, problem_folder, problem_id)

    # Extract and log test coverage
    first_five_coverage, total_coverage = extract_coverage_percentages(problem_folder, problem_name)

    # Log results
    log_results(problem_folder, first_five_coverage_report, total_coverage_report, test_results, logger, num_input_tokens, num_output_tokens)

    return first_five_coverage, total_coverage, accuracy, num_input_tokens, num_output_tokens


def process_problem(problem, model, dataset, log_folder, code_architect_prompt, test_generator_prompt):
    try:
        curr_first_five_coverage_percentage, curr_total_coverage_percentage, accuracy_percentage, curr_num_input_tokens, curr_num_output_tokens = qaAgent(problem, dataset, model, code_architect_prompt, test_generator_prompt)
        return problem["task_id"], curr_num_input_tokens, curr_num_output_tokens, curr_first_five_coverage_percentage, curr_total_coverage_percentage, accuracy_percentage
    except Exception as e:
        logger.error(f'Error in problem ID {problem["task_id"]}: {e}')
        with open(os.path.join(log_folder, 'errors.txt'), 'a') as f:
            f.write(f'Error in problem ID {problem["task_id"]}: {e}\n')
        return problem["task_id"], 0, 0, 0.0, 0.0, 0.0  # Return 0 tokens if there's an error

if __name__ == "__main__":
    args = parse_args()

    # Setup
    model = args.model
    dataset = args.dataset
    log_folder = create_log_folder()
    logger = setup_logger(log_folder)

    # Load prompts and problems
    prompt_paths = {
        "humaneval": { "code_architect": "prompts/v1/code_architect_humaneval_prompt.txt", "test_generator": "prompts/v1/test_generator_humaneval_prompt.txt" },
        "mbpp": { "code_architect": "prompts/v1/code_architect_mbpp_prompt.txt", "test_generator": "prompts/v1/test_generator_mbpp_prompt.txt" }
    }
    code_architect_prompt = prompt_paths[args.dataset]["code_architect"]
    test_generator_prompt = prompt_paths[args.dataset]["test_generator"]

    # Load dataset
    dataset_map = {
        "humaneval": "datasets/humaneval/problems.jsonl",
        "mbpp": "datasets/mbpp/problems.jsonl"
    }
    problems = read_problems(dataset_map[args.dataset])
    print(f"Loaded problems from: {dataset_map[args.dataset]}")

    # Initialize statistics
    total_stats = {
        'input_tokens': 0,
        'output_tokens': 0,
        'first_five_coverage': 0.0,
        'coverage': 0.0,
        'accuracy': 0.0,
        'evaluated': 0
    }

    # Run the QaAgent function on each problem
    start_index = 0
    end_index = 164 if args.dataset == "humaneval" else 500
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit all problems to the executor
        future_to_problem = {executor.submit(process_problem, problems[i], model, args.dataset, log_folder, code_architect_prompt, test_generator_prompt): i for i in
                             range(start_index, end_index)}
        for future in concurrent.futures.as_completed(future_to_problem):
            problem_index = future_to_problem[future]
            try:
                result= future.result()
                if result:
                    update_total_stats(result, total_stats)
                    write_summary(log_folder, total_stats)
                    write_details(log_folder, result)
            except Exception as e:
                logger.error(f"Error processing problem: {e}")

