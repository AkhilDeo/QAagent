from src.QAagent.utils.processing import process_block
from src.QAagent.tools.call_and_handle import call_and_handle
import time

def architect_code(problem, prompt_path, model):
    with open(prompt_path, "r") as f2:
        architect_prompt = f2.read()
        problem_prompt = problem["prompt"]

        full_code_architect_prompt = f"""
        {architect_prompt}

        ## Prompt 3:
        ```
        {problem_prompt}
        ```
        ## Completion 3:
        """
        messages = [{"role": "system", "content": "You are a software programmer."},
                    {"role": "user", "content": full_code_architect_prompt}]
        try:
            pseudocode, input_token_count, output_token_count = call_and_handle(messages, model)
            return process_block(pseudocode.choices[0].message.content), input_token_count, output_token_count

        except Exception as e:
            print(e)
            time.sleep(10)
            completion = ""