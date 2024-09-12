import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_and_handle(messages, model):
    # Get the encoding for the model

    # Call the model to get the completion
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    # Count output tokens
    print(completion.choices[0].message.content)
    input_token_count = completion.usage.prompt_tokens
    output_token_count = completion.usage.completion_tokens

    return completion, input_token_count, output_token_count