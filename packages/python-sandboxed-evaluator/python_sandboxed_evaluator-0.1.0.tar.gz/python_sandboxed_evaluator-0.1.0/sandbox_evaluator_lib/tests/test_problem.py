import unittest
from sandbox_evaluator_lib.problem import Problem
from sandbox_evaluator_lib.sandbox_evaluator import SandboxEvaluator


class TestProblem(unittest.TestCase):
    def setUp(self):
        # Initialize the evaluator and the problem instance
        self.evaluator = SandboxEvaluator(time_limit=1, memory_limit=10 * 1024 * 1024)

    def test_problem_validation_success(self):
        test_cases = [
            {"input": {"x": 5, "y": 7}, "expected_output": 12},
            {"input": {"x": 2, "y": 3}, "expected_output": 5},
        ]
        user_code = """
result = x + y
"""
        
        # Create a problem instance
        problem = Problem("Sum two numbers", user_code, test_cases)
        
        # Validate the problem (i.e., evaluate code for all test cases)
        validation_results = problem.validate()

        # Check that all test cases pass
        for case in validation_results:
            self.assertTrue(case["passed"], f"Failed for input {case['input']}")

    def test_problem_validation_failure(self):
        test_cases = [
            {"input": {"x": 5, "y": 7}, "expected_output": 12},
            {"input": {"x": 2, "y": 3}, "expected_output": 6},  # Invalid expected result
        ]
        user_code = """
result = x + y
"""
        
        # Create a problem instance
        problem = Problem("Sum two numbers", user_code, test_cases)
        
        # Validate the problem (i.e., evaluate code for all test cases)
        validation_results = problem.validate()

        # Check that second test case fails
        failed_cases = [case for case in validation_results if not case["passed"]]
        self.assertEqual(len(failed_cases), 1, "Expected one failed test case.")
        self.assertEqual(failed_cases[0]["error"], None, "Error message should be None.")

    def test_problem_syntax_error(self):
        test_cases = [
            {"input": {"x": 5, "y": 7}, "expected_output": 12},
        ]
        # Invalid user code with syntax error
        user_code = """
def invalid_code
    pass
"""
        
        # Create a problem instance
        problem = Problem("Test for syntax error", user_code, test_cases)
        
        # Validate the problem (i.e., evaluate code for all test cases)
        validation_results = problem.validate()

        # Check that the syntax error is correctly captured
        failed_cases = [case for case in validation_results if not case["passed"]]
        self.assertEqual(len(failed_cases), 1, "Expected one failed test case due to syntax error.")
        self.assertIn("invalid syntax", failed_cases[0]["error"])

    def test_problem_invalid_input(self):
        test_cases = [
            {"input": {"x": object()}, "expected_output": None},  # Invalid input type
        ]
        user_code = """
result = x
"""
        
        # Create a problem instance
        problem = Problem("Test for invalid input", user_code, test_cases)
        
        # Validate the problem (i.e., evaluate code for all test cases)
        validation_results = problem.validate()

        # Check that the validation fails due to invalid input type
        failed_cases = [case for case in validation_results if not case["passed"]]
        self.assertEqual(len(failed_cases), 1, "Expected one failed test case due to invalid input.")
        self.assertIn("Invalid inputs provided", failed_cases[0]["error"])

    def test_problem_memory_limit(self):
        test_cases = [
            {"input": {"x": 100}, "expected_output": "Memory overflow"},  # Potential memory overflow
        ]
        user_code = """
result = [0] * (10**8)  # This should exceed memory limits
"""
        
        # Create a problem instance
        problem = Problem("Test for memory overflow", user_code, test_cases)
        
        # Validate the problem (i.e., evaluate code for all test cases)
        validation_results = problem.validate()

        # Check if memory overflow error is captured
        failed_cases = [case for case in validation_results if not case["passed"]]
        self.assertEqual(len(failed_cases), 1, "Expected one failed test case due to memory overflow.")

if __name__ == "__main__":
    unittest.main()
