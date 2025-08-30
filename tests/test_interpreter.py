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

    def test_error_conditions(self):
        """Test various error conditions in interpreter."""
        import pytest

        from chronostack.interpreter import InterpreterError

        # Push operation on empty stack
        with pytest.raises(InterpreterError, match="Push requires a value on the stack"):
            self.execute_code("push")

        # Dup operation on empty stack
        with pytest.raises(InterpreterError, match="Dup requires value on stack"):
            self.execute_code("dup")

        # Swap with insufficient stack
        with pytest.raises(InterpreterError, match="Swap requires two values"):
            self.execute_code("1 swap")

        # Rot with insufficient stack
        with pytest.raises(InterpreterError, match="Rot requires three values"):
            self.execute_code("1 2 rot")

        # Math operations on empty stack
        with pytest.raises(InterpreterError, match="requires two values"):
            self.execute_code("1 +")

        # Comparison operations on empty stack
        with pytest.raises(InterpreterError, match="requires two values"):
            self.execute_code("1 <")

        # Logical operations on empty stack
        with pytest.raises(InterpreterError, match="requires two values"):
            self.execute_code("1 and")

        # If without condition
        with pytest.raises(InterpreterError, match="If requires condition"):
            self.execute_code("[ 42 ] if")

        # Loop without count
        with pytest.raises(InterpreterError, match="Loop requires count"):
            self.execute_code("[ 42 ] loop")

        # Division by zero
        with pytest.raises(InterpreterError, match="Division by zero"):
            self.execute_code("5 0 /")

        # Modulo by zero
        with pytest.raises(InterpreterError, match="Modulo by zero"):
            self.execute_code("5 0 %")

    def test_temporal_operations_comprehensive(self):
        """Test comprehensive temporal operations."""
        # Test branch with string name
        interpreter = self.execute_code('42 tick "test-branch" branch')
        stack = interpreter.current_stack()
        assert "test-branch" in str(stack)  # Should return branch name

        # Test branch without name (auto-generated)
        interpreter = self.execute_code("42 tick branch")
        stack = interpreter.current_stack()
        assert len(stack) > 0  # Should have branch name

        # Test merge with target branch
        interpreter = self.execute_code('42 tick "test" branch "main" merge')
        stack = interpreter.current_stack()
        assert len(stack) > 0  # Should have merge result

        # Test merge without target (merge to parent)
        interpreter = self.execute_code('42 tick "test" branch merge')
        stack = interpreter.current_stack()
        assert len(stack) > 0  # Should have merge result

        # Test paradox resolution
        interpreter = self.execute_code("10 tick 99 2 send paradox!")
        stack = interpreter.current_stack()
        assert isinstance(stack[-1], int)  # Should have resolved count

    def test_fixed_point_paradox_resolution_integration(self):
        """Test fixed-point paradox resolution through interpreter."""
        from chronostack.parser import OperationNode
        from chronostack.lexer import TokenType
        
        interpreter = Interpreter()

        # Create a paradox scenario
        interpreter.push(10)
        interpreter.execute_operation(OperationNode("tick", TokenType.TICK))
        interpreter.push(20) 
        interpreter.execute_operation(OperationNode("tick", TokenType.TICK))
        
        # Send value back to create paradox
        interpreter.push(99)
        interpreter.push(1)
        interpreter.execute_operation(OperationNode("send", TokenType.SEND))
        assert interpreter.pop()  # Should return True for successful send
        
        # Verify paradox exists
        assert interpreter.timeline.has_paradoxes()
        
        # Test that we can resolve using fixed-point strategy directly
        paradoxes = interpreter.timeline.detect_paradoxes()
        moment_index = paradoxes[0][0]
        
        success = interpreter.timeline.resolve_paradox(moment_index, "fixed_point")
        assert success
        assert not interpreter.timeline.has_paradoxes()

    def test_advanced_temporal_operations(self):
        """Test advanced temporal operations like echo and send."""
        # Test echo operation
        interpreter = self.execute_code("10 tick 20 tick 1 echo")
        stack = interpreter.current_stack()
        assert 10 in stack  # Should echo value from past

        # Test send operation
        interpreter = self.execute_code("10 tick 20 tick 99 1 send")
        # Should create temporal modification

    def test_peek_future_operation(self):
        """Test peek-future operation."""
        interpreter = self.execute_code("10 tick 1 peek-future")
        interpreter.current_stack()
        # Should have peeked into future

    def test_advanced_control_flow(self):
        """Test advanced control flow operations."""
        import pytest

        from chronostack.interpreter import InterpreterError

        # Test when-stable with stable timeline
        interpreter = self.execute_code("[ 42 ] when-stable")
        stack = interpreter.current_stack()
        assert 42 in stack  # Should execute because timeline is stable

        # Test when-stable error conditions
        with pytest.raises(InterpreterError, match="When-stable requires code block"):
            self.execute_code("when-stable")

        with pytest.raises(InterpreterError, match="When-stable requires code block"):
            self.execute_code("42 when-stable")  # Not a code block

        # Test if with error conditions
        with pytest.raises(InterpreterError, match="If requires condition and code block"):
            self.execute_code("if")

        with pytest.raises(InterpreterError, match="If requires code block"):
            self.execute_code("1 42 if")  # 42 is not a code block

        # Test loop with error conditions
        with pytest.raises(InterpreterError, match="Loop requires count and code block"):
            self.execute_code("[ 42 ] loop")  # Missing count

        with pytest.raises(InterpreterError, match="Loop requires positive integer count"):
            self.execute_code('"not-int" [ 42 ] loop')  # Non-integer count

        with pytest.raises(InterpreterError, match="Loop requires positive integer count"):
            self.execute_code("-1 [ 42 ] loop")  # Negative count

        with pytest.raises(InterpreterError, match="Loop requires code block"):
            self.execute_code("3 42 loop")  # Not a code block

    def test_temporal_fold_and_ripple(self):
        """Test comprehensive temporal-fold and ripple operations."""
        # Test temporal-fold with various operations
        interpreter = self.execute_code('10 tick 20 tick 30 tick "sum" temporal-fold')
        results = interpreter.current_stack()[-1]
        assert isinstance(results, list)
        
        interpreter = self.execute_code('10 tick 20 tick 30 tick "count" temporal-fold')
        results = interpreter.current_stack()[-1]
        assert isinstance(results, list)
        
        interpreter = self.execute_code('10 tick 20 tick 30 tick "max" temporal-fold')
        results = interpreter.current_stack()[-1]
        assert isinstance(results, list)

        # Test ripple with different operations
        interpreter = self.execute_code('10 tick 20 tick 30 tick 2 rewind pop "push" 999 ripple')
        # Should push 999 to all future moments
        
        interpreter = self.execute_code('10 tick 20 tick 30 tick 1 rewind pop "multiply" 2 ripple')
        # Should multiply top values in future moments by 2
        
        interpreter = self.execute_code('10 tick 20 tick 30 tick 1 rewind pop "clear" 0 ripple')
        # Should clear all future moments

    def test_enhanced_temporal_operations_comprehensive(self):
        """Test all enhanced temporal operations with error handling."""
        import pytest
        
        from chronostack.interpreter import InterpreterError

        # Test temporal-fold requires operation string
        with pytest.raises(InterpreterError, match="Temporal-fold requires operation string"):
            self.execute_code("temporal-fold")
            
        # Test temporal-fold with invalid operation type
        with pytest.raises(InterpreterError, match="Temporal-fold requires string operation"):
            self.execute_code("42 temporal-fold")

        # Test ripple requires operation and value
        with pytest.raises(InterpreterError, match="Ripple requires operation and value"):
            self.execute_code("ripple")
            
        with pytest.raises(InterpreterError, match="Ripple requires operation and value"):
            self.execute_code("42 ripple")

        # Test ripple with invalid operation type
        with pytest.raises(InterpreterError, match="Ripple requires string operation"):
            self.execute_code("42 100 ripple")

        # Test successful operations
        interpreter = self.execute_code('5 10 15 tick "sum" temporal-fold')
        results = interpreter.current_stack()[-1]
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_temporal_operations_with_branching(self):
        """Test temporal operations work correctly with timeline branching."""
        # Create a timeline with branching
        interpreter = self.execute_code('10 tick 20 tick branch "test" 30 tick "count" temporal-fold')
        
        # Test temporal-fold works with branches
        results = interpreter.current_stack()[-1]
        assert isinstance(results, list)
        
        # Test ripple works with branches - create fresh interpreter
        interpreter = self.execute_code('10 tick 20 tick branch "test" 30 tick 1 rewind pop "push" 999 ripple')
        # Should affect future moments in current branch

    def parse_statement(self, code_str):
        """Helper to parse a single statement."""
        from chronostack.lexer import Lexer
        from chronostack.parser import Parser
        
        lexer = Lexer(code_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return ast.statements[0]

    def test_unknown_operations(self):
        """Test unknown operation handling."""
        # Test that unknown symbols just get pushed as literals
        interpreter = self.execute_code("unknown-symbol")
        stack = interpreter.current_stack()
        assert "unknown-symbol" in stack

    def test_stack_error_conditions(self):
        """Test stack operation error conditions."""
        import pytest

        from chronostack.interpreter import InterpreterError

        # Test pop from empty stack
        interpreter = Interpreter()
        with pytest.raises(InterpreterError, match="Cannot pop from empty stack"):
            interpreter.pop()

        # Test peek at empty stack
        with pytest.raises(InterpreterError, match="Cannot peek at empty stack"):
            interpreter.peek()

    def test_interpreter_state_methods(self):
        """Test interpreter state and utility methods."""
        interpreter = Interpreter()

        # Test initial state
        assert interpreter.current_stack() == []
        assert interpreter.get_stack_display() == "[]"

        # Test with values
        interpreter.push(42)
        interpreter.push("hello")

        # Test truthy evaluation with various types
        assert interpreter.is_truthy(1)
        assert not interpreter.is_truthy(0)
        assert interpreter.is_truthy("hello")
        assert not interpreter.is_truthy("")
        assert interpreter.is_truthy([1, 2])
        assert not interpreter.is_truthy([])
        assert not interpreter.is_truthy(None)
        assert interpreter.is_truthy({"key": "value"})  # Other objects are truthy

    def test_word_execution_with_recursion(self):
        """Test word execution including call stack management."""
        # Test that recursive calls are properly detected
        interpreter = Interpreter()
        interpreter.words["test"] = []  # Empty word definition

        # Manually trigger recursive call detection
        interpreter.call_stack.append("test")
        import pytest

        from chronostack.interpreter import InterpreterError

        with pytest.raises(InterpreterError, match="Recursive call detected"):
            interpreter.execute_word("test")
