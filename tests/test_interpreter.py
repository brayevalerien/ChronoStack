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

    def test_comprehensive_arithmetic(self):
        """Test all arithmetic operations."""
        # Division
        interpreter = self.execute_code("10 2 /")
        assert interpreter.current_stack() == [5]

        # Modulo
        interpreter = self.execute_code("10 3 %")
        assert interpreter.current_stack() == [1]

        # Multiple operations
        interpreter = self.execute_code("2 3 * 4 + 5 /")  # (2*3+4)/5 = 10/5 = 2
        assert interpreter.current_stack() == [2]

    def test_comparison_operations(self):
        """Test comparison operations."""
        interpreter = self.execute_code("5 3 <")
        assert interpreter.current_stack() == [0]  # false

        interpreter = self.execute_code("3 5 <")
        assert interpreter.current_stack() == [1]  # true

        interpreter = self.execute_code("5 3 >")
        assert interpreter.current_stack() == [1]  # true

        interpreter = self.execute_code("5 5 =")
        assert interpreter.current_stack() == [1]  # true

    def test_logical_operations(self):
        """Test logical operations."""
        interpreter = self.execute_code("1 1 and")
        assert interpreter.current_stack() == [1]

        interpreter = self.execute_code("1 0 and")
        assert interpreter.current_stack() == [0]

        interpreter = self.execute_code("1 0 or")
        assert interpreter.current_stack() == [1]

        interpreter = self.execute_code("1 not")
        assert interpreter.current_stack() == [0]

    def test_rot_operation(self):
        """Test rot (rotate) operation."""
        interpreter = self.execute_code("1 2 3 rot")
        assert interpreter.current_stack() == [2, 3, 1]

    def test_loop_operation(self):
        """Test loop operation."""
        interpreter = self.execute_code("3 [ 5 ] loop")
        assert interpreter.current_stack() == [5, 5, 5]

    def test_code_block_execution(self):
        """Test code block execution."""
        interpreter = self.execute_code("[ 1 2 + ]")
        assert len(interpreter.current_stack()) == 1
        # Code block should be on stack as a list

    def test_string_handling(self):
        """Test string literals."""
        interpreter = self.execute_code('"hello" "world"')
        assert interpreter.current_stack() == ["hello", "world"]

    def test_symbol_handling(self):
        """Test symbol literals."""
        interpreter = self.execute_code(":test")
        assert interpreter.current_stack() == [":test"]

    def test_peek_operation(self):
        """Test peek operation (internal method)."""
        interpreter = Interpreter()
        interpreter.push(42)
        assert interpreter.peek() == 42
        assert interpreter.current_stack() == [42]  # Should not modify stack

    def test_get_stack_display(self):
        """Test stack display formatting."""
        interpreter = Interpreter()
        assert interpreter.get_stack_display() == "[]"

        interpreter.push(42)
        interpreter.push("hello")
        display = interpreter.get_stack_display()
        assert "42" in display
        assert "hello" in display

    def test_temporal_rewind(self):
        """Test temporal rewind functionality."""
        interpreter = self.execute_code("42 tick 99 tick 1 rewind")
        # After rewind, should be back at the previous moment
        stack = interpreter.current_stack()
        assert 42 in stack  # Should have the earlier value

    def test_pop_operation(self):
        """Test explicit pop operation."""
        interpreter = self.execute_code("1 2 3 pop")
        assert interpreter.current_stack() == [1, 2]
