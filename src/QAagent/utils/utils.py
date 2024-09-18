import json
import argparse
from typing import Dict, Iterable

def read_problems(filename: str) -> list:
    return list(stream_jsonl(filename))

def stream_jsonl(filename: str) -> Iterable[Dict]:
    # Parses each jsonl line from a .jsonl file and yields it as a dictionary.
    with open(filename, "r") as fp:
        for line in fp:
            if any(not x.isspace() for x in line):
                yield json.loads(line)


def add_plan(problem_name, pseudocode):
    return f"""{problem_name["prompt"]}

{pseudocode}
"""

def add_canonical_solution(problem_name):
    return f"""{problem_name["prompt"]}
{problem_name["canonical_solution"]}
"""

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

def update_total_stats(result, total_stats):
    problem_id, cur_num_input_tokens, cur_num_output_tokens, cur_first_five_coverage, cur_total_coverage, cur_accuracy = result
    total_stats['input_tokens'] += cur_num_input_tokens
    total_stats['output_tokens'] += cur_num_output_tokens
    total_stats['first_five_coverage'] += cur_first_five_coverage
    total_stats['coverage'] += cur_total_coverage
    total_stats['accuracy'] += cur_accuracy
    total_stats['evaluated'] += 1