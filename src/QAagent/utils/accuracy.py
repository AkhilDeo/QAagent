from io import StringIO

def get_accuracy(canonical_solution, tests, log_folder, problem_id):
    # Run the tests

    test_result = StringIO()
    passed_tests = 0
    total_tests = 0

    local_scope = {}
    exec(canonical_solution, globals())  # Execute the canonical solution

    # Split the tests into individual lines
    individual_tests = tests.strip().split('\n')

    for test in individual_tests:
        test = test.strip()  # Remove leading and trailing whitespaces

        # Skip blank lines and comments
        if not test or test.startswith('#'):
            continue

        # Only count assert statements
        if not test.startswith('assert'):
            test_result.write(f"Skipping non-assert statement: {test}\n")
            continue

        total_tests += 1

        try:
            # Execute the canonical solution followed by the test case
            # print("TEST:")
            # print(canonical_solution + '\n' + test)
            # exec(canonical_solution + '\n' + test, globals(), local_scope)
            exec(test, globals())
            passed_tests += 1  # Increment passed tests if no exception occurs
        except AssertionError:
            test_result.write(f"Test failed: {test}\n")
        except Exception as e:
            test_result.write(f"An error occurred during test '{test}': {str(e)}\n")

    # Calculate percentage of passed tests
    accuracy = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    test_result.write(f"\nPassed {passed_tests}/{total_tests} tests ({accuracy:.2f}%)\n")

    return accuracy, test_result.getvalue()