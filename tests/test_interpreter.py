"""Basic tests for the ChronoStack interpreter."""

from chronostack.interpreter import Interpreter
from chronostack.lexer import Lexer
from chronostack.parser import Parser


class TestInterpreter:
    """Test cases for the interpreter."""

    def execute_code(self, code: str) -> Interpreter:
        """Helper to execute ChronoStack code and return interpreter."""
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        interpreter = Interpreter()
        interpreter.execute_program(ast)
        return interpreter

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        interpreter = self.execute_code("5 3 +")
        assert interpreter.current_stack() == [8]

        interpreter = self.execute_code("10 4 - 2 *")
        assert interpreter.current_stack() == [12]  # (10-4)*2

    def test_stack_operations(self):
        """Test stack manipulation operations."""
        interpreter = self.execute_code("1 2 3 dup")
        assert interpreter.current_stack() == [1, 2, 3, 3]

        interpreter = self.execute_code("1 2 swap")
        assert interpreter.current_stack() == [2, 1]

    def test_temporal_operations(self):
        """Test temporal operations."""
        interpreter = self.execute_code("42 tick")
        # Should have 42 and timestamp on stack
        assert len(interpreter.current_stack()) == 2
        assert interpreter.current_stack()[0] == 42
        assert isinstance(interpreter.current_stack()[1], int)

    def test_word_definition(self):
        """Test word definitions and calls."""
        interpreter = self.execute_code(":double dup + ; 5 double")
        assert interpreter.current_stack() == [10]

    def test_control_flow(self):
        """Test control flow operations."""
        interpreter = self.execute_code("1 [ 42 ] if")
        assert interpreter.current_stack() == [42]

        interpreter = self.execute_code("0 [ 42 ] if")
        assert interpreter.current_stack() == []
