import os
import logging
from datetime import datetime


def write_plan_and_tests_qa(log_folder, problem_id, pseudocode, tests):
    # Write results to files
    result_folder = os.path.join(log_folder, f'problem_{problem_id}')
    os.makedirs(result_folder, exist_ok=True)

    with open(os.path.join(result_folder, 'pseudocode.txt'), 'w') as f:
        f.write(pseudocode)

    with open(os.path.join(result_folder, 'generated_tests.txt'), 'w') as f:
        f.write(tests)

def write_domain_and_tests_qa(log_folder, problem_id, domain, tests):
    # Write results to files
    result_folder = os.path.join(log_folder, f'problem_{problem_id}')
    os.makedirs(result_folder, exist_ok=True)

    with open(os.path.join(result_folder, 'domain.txt'), 'w') as f:
        f.write(domain)

    with open(os.path.join(result_folder, 'generated_tests.txt'), 'w') as f:
        f.write(tests)

def create_log_folder():
    """Creates a timestamped folder for logs."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_folder = os.path.join('logs', f'QAagent-{timestamp}')
    os.makedirs(log_folder, exist_ok=True)
    return log_folder

def setup_logger(log_folder):
    """Sets up the logger to log into the timestamped folder."""
    logger = logging.getLogger('QAagentLogger')
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(os.path.join(log_folder, 'QAagent.log'))
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


def log_results(problem_folder, first_five_coverage_report, total_coverage_report, test_results, logger, num_input_tokens, num_output_tokens):
    """Logs results and writes them to files."""
    with open(os.path.join(problem_folder, 'test_results_accuracy.txt'), 'w') as f:
        f.write(test_results)

    with open(os.path.join(problem_folder, 'first_five_coverage_report.txt'), 'w') as f:
        f.write(first_five_coverage_report)

    with open(os.path.join(problem_folder, 'total_coverage_report.txt'), 'w') as f:
        f.write(total_coverage_report)

    logger.info(f'Number of input tokens: {num_input_tokens}\nNumber of output tokens: {num_output_tokens}')

    print("Test Results:")
    print(test_results)
    print("\nFirst Five Coverage Report:")
    print(first_five_coverage_report)
    print("\nTotal Five Coverage Report:")
    print(total_coverage_report)

def write_summary(log_folder, total_stats):
    evaluated = total_stats['evaluated']
    with open(os.path.join(log_folder, 'summary.txt'), 'w') as summary_file:
        summary_file.write(
            f"Accuracy: {total_stats['accuracy'] / evaluated}\n"
            f"First five coverage: {total_stats['first_five_coverage'] / evaluated}\n"
            f"Coverage: {total_stats['coverage'] / evaluated}\n"
            f"Input tokens: {total_stats['input_tokens']}\nOutput tokens: {total_stats['output_tokens']}\n")

def write_details(log_folder, result):
    problem_id, cur_num_input_tokens, cur_num_output_tokens, cur_first_five_coverage, cur_total_coverage, cur_accuracy = result
    with open(os.path.join(log_folder, 'details.txt'), 'a') as details_file:
        details_file.write(
            f"Problem ID: {problem_id}\nAccuracy: {cur_accuracy}\n"
            f"First five coverage: {cur_first_five_coverage}\n"
            f"Coverage: {cur_total_coverage}\n"
            f"Input tokens: {cur_num_input_tokens}\nOutput tokens: {cur_num_output_tokens}\n")