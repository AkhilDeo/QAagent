import json
from typing import Dict, Iterable


def read_problems(filename: str) -> list:
    return list(stream_jsonl(filename))

def stream_jsonl(filename: str) -> Iterable[Dict]:
    # Parses each jsonl line from a .jsonl file and yields it as a dictionary.
    with open(filename, "r") as fp:
        for line in fp:
            if any(not x.isspace() for x in line):
                yield json.loads(line)