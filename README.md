# QAagent: A Multiagent System for Unit Test Generation via Natural Language Pseudocode

---

QAagent is a multiagent system that leverages LLMs’ abilities to write pseudocode for functions in code to improve the coverage of generated unit tests. This technique can be utilized in autonomous and agentic code generation systems. The framework consists of two agents: a Code Architect Agent and a Test Generator Agent. These agents work together to assume how a snippet of code will be implemented without having access to the code itself, and then generate unit tests for the code.

### Code Architect Agent
QAagent's first agent, the architect agent, thinks in a step-by-step fashion how an unimplemented snippet of code will likely be completed. The agent is only given a function header and some details about the aim of function, and outputs natural langauge pseudocode.

### Test Generator Agent
After the code architect agent is done, the test generator agent takes the pseudocode, as well as the function header and the comment for the function header, and generates unit tests for the function. The pseudocode enables the LLM to generate tests with greater coverage than existing unit test generation methodologies.

## Results of QAagent on 2 Benchmarks

We evaluated QAagent on test generation on problems from two benchmarks: Humaneval and MBPP. The results are shown below.

### Coverage

| **Model**      | **Approach**  | **Humaneval** | **MBPP**   |
|----------------| --------      |-----------|------------|
| ChatGPT        | Direct       | 67.1      | 58.4       |
| GPT-3.5 Turbo  | Direct       | 70.2      | 61.3       |
| -              | CodeCoT      | 77.2      | 82.9       |
| GPT-3.5 Turbo  | AgentCoder   | 87.5      | 89.5       |
| GPT-4          | MetaGPT      | 81.7      | 80.5       |
| GPT-4          | AgentCoder   | 91.7      | 92.3       |
| GPT-4 Turbo    | QAagent      | 96.6      | 87.9       |

### Accuracy

| **Model**     | **Approach** | **Humaneval** | **MBPP** |
|---------------|--------------|---------------|----------|
| GPT-3.5 Turbo | Direct       | 47.0          | 57.2     |
| -             | CodeCoT      | 67.1          | 79.0     |
| GPT-3.5 Turbo | AgentCoder   | 87.8          | 89.9     |
| GPT-4         | MetaGPT      | 79.3          | 84.4     |
| GPT-4         | AgentCoder   | 89.6          | 91.4     |
| GPT-4 Turbo   | QAagent      | 88.6          | 52.7     |

## Installation

To use QAagent, first ensure that you have an API key from OpenAI. QAagent has only been tested with `GPT-4`, `GPT-4-Turbo`, and `GPT-4o`.

1. Clone the QAagent repository in your home directory
```bash
cd ~
git clone https://github.com/AkhilDeo/QAagent.git
cd QAagent
```

2. Add python to your path

If you use bash:
```bash
echo 'export PYTHONPATH="~/QAagent/:$PYTHONPATH"' >> ~/.bashrc && source ~/.bashrc
```

If you use zsh:
```zsh
echo 'export PYTHONPATH="~/QAagent/:$PYTHONPATH"' >> ~/.zshrc && source ~/.zshrc
```

3. Install the required packages
```bash
pip install -r requirements.txt
```

4. Create a `.env` file and set your OpenAI API key. This command creates the `.env`, update the `.env` with your API key.
```bash
touch .env
echo 'OPENAI_API_KEY=your-api-key-here' >> .env
```

5. Run QAagent to generate tests. An example is given below.

```bash
python3 src/QAagent/QAagent.py --dataset humaneval --model gpt-4o
```

Dataset can be `humaneval` or `mbpp` and model can be any valid OpenAI model ID, but has only been tested with `gpt-4`, `gpt-4-turbo`, and `gpt-4o`.
