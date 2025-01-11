import logging
import multiprocessing
import resource
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define helper functions at the top level for pickling
def getitem(obj, index):
    return obj[index]

def write(obj):
    return obj

def restricted_execution(pipe, code, inputs, memory_limit, safe_globals):
    """Executes code in a restricted environment within a separate process."""
    try:
        # Set the memory limit for the process
        memory_limit = resource.getrlimit(resource.RLIMIT_AS)
        memory_limit = min(memory_limit[1], memory_limit[0] + memory_limit[1])
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

        # Compile the user-provided code
        byte_code = compile_restricted(code, filename="<string>", mode="exec")

        # Update the globals with the provided inputs
        safe_globals.update(inputs)

        # Execute the code
        exec(byte_code, safe_globals)

        # Collect the result (return only non-private variables)
        result = {key: safe_globals[key] for key in safe_globals if not key.startswith("_")}

        # Send the result back through the pipe
        pipe.send({"success": True, "result": result})
    except Exception as e:
        logging.error("Error during execution: %s", str(e))
        pipe.send({"success": False, "error": str(e)})
    finally:
        pipe.close()


class SandboxEvaluator:
    def __init__(self, time_limit=2, memory_limit=100 * 1024 * 1024):
        """
        Initializes the sandbox evaluator.

        Args:
            time_limit (int): Maximum execution time in seconds.
            memory_limit (int): Maximum memory usage in bytes.
        """
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.safe_globals = {
            "__builtins__": safe_builtins,
            "_print_": print,
            "_getattr_": getattr,
            "_setattr_": setattr,
            "_getitem_": getitem,
            "_write_": write,
        }

    def validate_inputs(self, inputs: dict) -> bool:
        """
        Validates the inputs provided to the sandbox.

        Args:
            inputs (dict): Input variables to validate.

        Returns:
            bool: True if inputs are valid, False otherwise.
        """
        for key, value in inputs.items():
            if not isinstance(value, (int, float, str, list, dict)):
                logging.error("Invalid input type for %s: %s", key, type(value))
                return False
        return True

    def evaluate(self, code: str, inputs: dict) -> dict:
        """
        Executes the provided Python code in a restricted environment.

        Args:
            code (str): The user-provided Python code.
            inputs (dict): Input variables to provide to the code.

        Returns:
            dict: A dictionary containing the result or error message.
        """
        if not self.validate_inputs(inputs):
            return {"success": False, "error": "Invalid inputs provided"}
        
        logging.info("Evaluating code with inputs: %s", inputs)

        # Create a Pipe for communication between the parent and child processes
        parent_conn, child_conn = multiprocessing.Pipe()

        # Create a separate process for restricted execution
        process = multiprocessing.Process(
            target=restricted_execution,
            args=(child_conn, code, inputs, self.memory_limit, self.safe_globals)
        )

        # Start the process
        process.start()

        try:
            # Wait for the result within the timeout limit
            if parent_conn.poll(self.time_limit):
                result_data = parent_conn.recv()
                logging.info("Execution result: %s", result_data)
                return result_data
            else:
                logging.warning("Execution time exceeded the limit")
                return {"success": False, "error": "Execution time exceeded the limit"}
        except Exception as e:
            logging.error("Error during execution: %s", str(e))
            return {"success": False, "error": str(e)}
        finally:
            # Ensure the process is terminated if it is still running
            if process.is_alive():
                process.terminate()
            process.join()

        # Return a generic error message if no result is received
        logging.error("Unknown error during execution")
        return {"success": False, "error": "Unknown error during execution"}
