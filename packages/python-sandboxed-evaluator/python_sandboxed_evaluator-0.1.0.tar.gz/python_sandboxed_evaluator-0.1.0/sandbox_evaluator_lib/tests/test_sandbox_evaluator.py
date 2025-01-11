import unittest
from sandbox_evaluator_lib.problem import Problem
from sandbox_evaluator_lib.sandbox_evaluator import SandboxEvaluator


class TestSandboxEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = SandboxEvaluator(time_limit=1, memory_limit=10 * 1024 * 1024)

    def test_normal_execution(self):
        code = "result = x + y"
        inputs = {"x": 5, "y": 7}
        result = self.evaluator.evaluate(code, inputs)
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["result"], 12)

    def test_timeout(self):
        code = "while True: pass"
        result = self.evaluator.evaluate(code, {})
        self.assertFalse(result["success"])
        self.assertIn("Execution time exceeded the limit", result["error"])

    def test_memory_overflow(self):
        code = "result = [0] * (10**8)"
        result = self.evaluator.evaluate(code, {})
        self.assertFalse(result["success"])

    def test_syntax_error(self):
        code = "def invalid_code"
        result = self.evaluator.evaluate(code, {})
        self.assertFalse(result["success"])
        self.assertIn("invalid syntax", result["error"])

    def test_invalid_input(self):
        code = "result = x"
        inputs = {"x": object()}
        result = self.evaluator.evaluate(code, inputs)
        self.assertFalse(result["success"])
        self.assertIn("Invalid inputs provided", result["error"])

if __name__ == "__main__":
    unittest.main()
