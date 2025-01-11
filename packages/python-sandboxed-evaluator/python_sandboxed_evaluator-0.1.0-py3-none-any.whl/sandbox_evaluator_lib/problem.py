from sandbox_evaluator_lib.sandbox_evaluator import SandboxEvaluator

class Problem:
    def __init__(self, description: str, user_code: str, test_cases: list):
        """
        Represents a programming problem with a user-defined solution.

        Args:
            description (str): Problem description.
            user_code (str): User-provided Python code.
            test_cases (list): Test cases with input and expected output.
        """
        self.description = description
        self.user_code = user_code
        self.test_cases = test_cases
        self.evaluator = SandboxEvaluator()

    def validate(self) -> list:
        """
        Validates the user-provided code against all test cases.

        Returns:
            list: A list of test results with input, expected output, result, and status.
        """
        results = []
        for case in self.test_cases:
            inputs = case["input"]
            expected_output = case["expected_output"]
            eval_result = self.evaluator.evaluate(self.user_code, inputs)
            
            # Check if execution was successful and matches expected output
            passed = eval_result["success"] and eval_result["result"].get("result") == expected_output
            
            results.append({
                "input": inputs,
                "expected_output": expected_output,
                "passed": passed,
                "error": eval_result.get("error") if not eval_result["success"] else None,
            })
        return results
