import unittest
import tempfile
import importlib
import os, json
import copy

class CodeTestResult(unittest.TestResult):
    """
    A test result class that stores the results of the tests
    """
    def __init__(self):
        super().__init__()
        self.test_results = []

    def addSuccess(self, test):
        self.test_results.append({
            'function_call': test.function_call,
            'expected_output': test.expected_output,
            'actual_output': test.actual_output,
            'pass': True
        })

    def addFailure(self, test, err):
        self.test_results.append({
            'function_call': test.function_call,
            'expected_output': test.expected_output,
            'actual_output': test.actual_output,
            'pass': False
        })

    def addError(self, test, err):
        self.test_results.append({
            'function_call': self.function_call,
            'expected_output': 'N/A',
            'actual_output': str(err),  # used to include the error traceback
            'pass': False
        })

class CodeRunner:
    """
    A test runner class that returns the results of the tests in a dictionary
    """
    def run(self, test_suite):
        result = CodeTestResult()
        test_suite.run(result)
        return result

class CodeFunctionTest(unittest.FunctionTestCase):
    """
    A test case class that runs a single test for a function
    """
    def __init__(self, function_call, args, expected_output, inplace=False):
        super().__init__(self.test_user_function)
        self.function_call = function_call
        self.args = args
        self.expected_output = expected_output
        self.actual_output = None
        self.inplace = inplace

    def test_user_function(self):
        global foo
        if not self.inplace:
            self.actual_output = foo(*self.args)
        else:
            self.actual_output = self.args[0].copy()
            foo(self.actual_output)
        assert self.actual_output == self.expected_output


class CodeTester:
    """
    A class that runs tests on a user's code with given test cases
    and returns the results of the tests in json format
    """

    def __init__(self, code, test_cases, inplace=False):
        self.code = code
        self.test_cases = test_cases
        self.current_test = None
        self.inplace = inplace


    def run_tests(self, verbosity=2, suppress_output=False):

        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp_file:
            temp_file.write(self.code.encode('utf-8'))
            temp_file_path = temp_file.name

        spec = importlib.util.spec_from_file_location("temp_module", temp_file_path)
        temp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(temp_module)

        os.remove(temp_file_path)

        globals()['foo'] = temp_module.foo

        test_suite = unittest.TestSuite()

        for test_case in self.test_cases:

            args, expected_output = test_case
            function_call = f"foo({', '.join(map(repr, args))})"

            cf_test = CodeFunctionTest(
                function_call=function_call,
                args=args,
                expected_output=expected_output,
                inplace=self.inplace
            )

            test_suite.addTest(cf_test)

        stream = open(os.devnull, 'w') if suppress_output else None

        runner = CodeRunner()
        result = runner.run(test_suite)

        if suppress_output:
            stream.close()

        return result
