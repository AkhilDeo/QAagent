import time
from src.QAagent.utils.processing import process_block
from src.QAagent.tools.call_and_handle import call_and_handle

def generate_test_code(problem, problem_id, prompt_path, model, logger):
    with open(prompt_path, "r") as f:
        test_generator_prompt = f.read()

        full_test_generator_prompt = f"""
        {test_generator_prompt}

        ## Prompt:
        ```
        {problem}
        ```

        ## Completion:
        """
        messages = [{"role": "system", "content": "You are a software programmer."},
                    {"role": "user", "content": full_test_generator_prompt}]
        try:
            generated_tests, input_token_count, output_token_count = call_and_handle(messages, model)
            print("RAW Generated tests: " + generated_tests.choices[0].message.content)
            logger.info("Task ID: " + problem_id + ": Generated tests: " + generated_tests.choices[0].message.content)
            return process_block(generated_tests.choices[0].message.content), input_token_count, output_token_count

        except Exception as e:
            print(e)
            time.sleep(10)
            completion = ""
            logger.info(f"Error: {e}")