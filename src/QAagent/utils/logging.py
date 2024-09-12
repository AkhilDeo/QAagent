import os


def write_plan_and_tests_qa(log_folder, problem_id, pseudocode, tests):
    # Write results to files
    result_folder = os.path.join(log_folder, f'problem_{problem_id}')
    os.makedirs(result_folder, exist_ok=True)

    with open(os.path.join(result_folder, 'pseudocode.txt'), 'w') as f:
        f.write(pseudocode)

    with open(os.path.join(result_folder, 'generated_tests.txt'), 'w') as f:
        f.write(tests)