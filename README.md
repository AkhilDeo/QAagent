# QAagent: A Multiagent System for Unit Test Generation via Natural Language Pseudocode

---

QAagent is a multiagent system that leverages LLMs’ abilities to write pseudocode for functions in code to improve the coverage of generated unit tests. This technique can be utilized in autonomous and agentic code generation systems. The framework consists of two agents: a Code Architect Agent and a Test Generator Agent. These agents work together to assume how a snippet of code will be implemented without having access to the code itself, and then generate unit tests for the code.

## Code Architect Agent
QAagent's first agent, the architect agent, thinks in a step-by-step fashion how an unimplemented snippet of code will likely be completed. The agent is only given a function header and some details about the aim of function, and outputs natural langauge pseudocode.

## Test Generator Agent
After the code architect agent is done, the test generator agent takes the pseudocode, as well as the function header and the comment for the function header, and generates unit tests for the function. The pseudocode enables the LLM to generate tests with greater coverage than existing unit test generation methodologies.