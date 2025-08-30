"""
Interpreter for ChronoStack - executes parsed programs with temporal stack operations.

The Interpreter class takes an AST and executes it, managing:
- Stack operations (push, pop, dup, swap, rot)
- Temporal operations (tick, rewind, peek-future, branch, merge, etc.)
- Math operations (+ - * / %)
- Comparison operations (< > =)
- Logical operations (and or not)
- Control flow (if, loop, when-stable)
- Word definitions and calls
"""

from typing import Any, Dict, List

from chronostack.lexer import TokenType
from chronostack.parser import (
    ASTNode,
    CodeBlockNode,
    LiteralNode,
    OperationNode,
    ProgramNode,
    WordDefinitionNode,
)
from chronostack.timeline import Timeline


class InterpreterError(Exception):
    """Exception raised during program execution."""

    pass


class Interpreter:
    """Executes ChronoStack programs with temporal stack operations."""

    def __init__(self):
        self.timeline = Timeline()
        self.words: Dict[str, List[ASTNode]] = {}  # User-defined words
        self.call_stack: List[str] = []  # For recursion detection

    def current_stack(self) -> List[Any]:
        """Get reference to current timeline stack."""
        return self.timeline.current_stack()

    def push(self, value: Any) -> None:
        """Push a value onto the stack."""
        self.current_stack().append(value)

    def pop(self) -> Any:
        """Pop and return the top value from the stack."""
        if not self.current_stack():
            raise InterpreterError("Cannot pop from empty stack")
        return self.current_stack().pop()

    def peek(self) -> Any:
        """Peek at the top value without removing it."""
        if not self.current_stack():
            raise InterpreterError("Cannot peek at empty stack")
        return self.current_stack()[-1]

    def execute_program(self, program: ProgramNode) -> None:
        """Execute a complete program."""
        for statement in program.statements:
            self.execute_statement(statement)

    def execute_statement(self, statement: ASTNode) -> None:
        """Execute a single statement."""
        if isinstance(statement, LiteralNode):
            self.execute_literal(statement)
        elif isinstance(statement, OperationNode):
            self.execute_operation(statement)
        elif isinstance(statement, CodeBlockNode):
            self.execute_code_block(statement)
        elif isinstance(statement, WordDefinitionNode):
            self.execute_word_definition(statement)
        else:
            raise InterpreterError(f"Unknown statement type: {type(statement)}")

    def execute_literal(self, literal: LiteralNode) -> None:
        """Execute a literal value."""
        if literal.token_type == TokenType.NUMBER or literal.token_type == TokenType.STRING:
            self.push(literal.value)
        elif literal.token_type == TokenType.SYMBOL:
            # Check if it's a user-defined word
            if literal.value in self.words:
                self.execute_word(literal.value)
            else:
                # Push symbol as literal value
                self.push(literal.value)
        else:
            raise InterpreterError(f"Unknown literal type: {literal.token_type}")

    def execute_operation(self, operation: OperationNode) -> None:
        """Execute an operation."""
        op = operation.operation

        # Stack operations
        if op == "push":
            # Push operation requires a value from the stack
            if not self.current_stack():
                raise InterpreterError("Push requires a value on the stack")
            # Push duplicates the top value (like dup)
            value = self.peek()
            self.push(value)

        elif op == "pop":
            if self.current_stack():
                self.pop()

        elif op == "dup":
            if not self.current_stack():
                raise InterpreterError("Dup requires value on stack")
            value = self.peek()
            self.push(value)

        elif op == "swap":
            if len(self.current_stack()) < 2:
                raise InterpreterError("Swap requires two values on stack")
            a = self.pop()
            b = self.pop()
            self.push(a)
            self.push(b)

        elif op == "rot":
            if len(self.current_stack()) < 3:
                raise InterpreterError("Rot requires three values on stack")
            c = self.pop()  # top
            b = self.pop()  # middle
            a = self.pop()  # bottom
            self.push(b)  # middle -> bottom
            self.push(c)  # top -> middle
            self.push(a)  # bottom -> top

        # Temporal operations
        elif op == "tick":
            timestamp = self.timeline.tick()
            self.push(timestamp)

        elif op == "rewind":
            if not self.current_stack():
                raise InterpreterError("Rewind requires number of steps")
            steps = self.pop()
            if not isinstance(steps, int) or steps < 0:
                raise InterpreterError("Rewind requires positive integer")
            timestamp = self.timeline.rewind(steps)
            self.push(timestamp)

        elif op == "peek-future":
            if not self.current_stack():
                raise InterpreterError("Peek-future requires number of steps")
            steps = self.pop()
            if not isinstance(steps, int) or steps < 0:
                raise InterpreterError("Peek-future requires positive integer")
            future_moment = self.timeline.peek_future(steps)
            if future_moment:
                # Push the top value from the future moment
                if future_moment.stack:
                    self.push(future_moment.stack[-1])
                else:
                    self.push(None)
            else:
                self.push(None)

        elif op == "branch":
            # Optionally pop branch name from stack
            if self.current_stack() and isinstance(self.peek(), str):
                branch_name = self.pop()
                new_branch = self.timeline.branch(branch_name)
            else:
                new_branch = self.timeline.branch()
            self.push(new_branch)

        elif op == "merge":
            # Optionally pop target branch name from stack
            if self.current_stack() and isinstance(self.peek(), str):
                target_branch = self.pop()
                success = self.timeline.merge(target_branch)
            else:
                success = self.timeline.merge()
            self.push(success)

        elif op == "paradox!":
            # Resolve all paradoxes using default strategy
            paradoxes = self.timeline.detect_paradoxes()
            resolved_count = 0
            for moment_index, _ in paradoxes:
                if self.timeline.resolve_paradox(moment_index):
                    resolved_count += 1
            self.push(resolved_count)

        elif op == "echo":
            if not self.current_stack():
                raise InterpreterError("Echo requires number of steps back")
            steps = self.pop()
            if not isinstance(steps, int) or steps < 0:
                raise InterpreterError("Echo requires positive integer")
            value = self.timeline.echo(steps)
            self.push(value)

        elif op == "send":
            if len(self.current_stack()) < 2:
                raise InterpreterError("Send requires value and number of steps")
            steps = self.pop()
            value = self.pop()
            if not isinstance(steps, int) or steps < 0:
                raise InterpreterError("Send requires positive integer steps")
            success = self.timeline.send(value, steps)
            self.push(success)

        elif op == "temporal-fold":
            if not self.current_stack():
                raise InterpreterError("Temporal-fold requires operation string")
            operation = self.pop()
            if not isinstance(operation, str):
                raise InterpreterError("Temporal-fold requires string operation")
            results = self.timeline.temporal_fold(operation)
            # Push results as a list
            self.push(results)

        elif op == "ripple":
            if len(self.current_stack()) < 2:
                raise InterpreterError("Ripple requires operation and value")
            value = self.pop()
            operation = self.pop()
            if not isinstance(operation, str):
                raise InterpreterError("Ripple requires string operation")
            self.timeline.ripple(operation, value)

        # Math operations
        elif op in ["+", "-", "*", "/", "%"]:
            self.execute_math_operation(op)

        # Comparison operations
        elif op in ["<", ">", "="]:
            self.execute_comparison_operation(op)

        # Logical operations
        elif op in ["and", "or", "not"]:
            self.execute_logical_operation(op)

        # Control flow
        elif op in ["if", "loop", "when-stable"]:
            self.execute_control_flow(op)

        else:
            raise InterpreterError(f"Unknown operation: {op}")

    def execute_math_operation(self, op: str) -> None:
        """Execute a math operation."""
        if len(self.current_stack()) < 2:
            raise InterpreterError(f"Math operation '{op}' requires two values")

        b = self.pop()
        a = self.pop()

        # Ensure numeric types
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise InterpreterError(f"Math operation '{op}' requires numeric values")

        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            if b == 0:
                raise InterpreterError("Division by zero")
            result = a / b
        elif op == "%":
            if b == 0:
                raise InterpreterError("Modulo by zero")
            result = a % b
        else:
            raise InterpreterError(f"Unknown math operation: {op}")

        self.push(result)

    def execute_comparison_operation(self, op: str) -> None:
        """Execute a comparison operation."""
        if len(self.current_stack()) < 2:
            raise InterpreterError(f"Comparison '{op}' requires two values")

        b = self.pop()
        a = self.pop()

        if op == "<":
            result = 1 if a < b else 0
        elif op == ">":
            result = 1 if a > b else 0
        elif op == "=":
            result = 1 if a == b else 0
        else:
            raise InterpreterError(f"Unknown comparison: {op}")

        self.push(result)

    def execute_logical_operation(self, op: str) -> None:
        """Execute a logical operation."""
        if op == "not":
            if not self.current_stack():
                raise InterpreterError("Not requires one value")
            value = self.pop()
            result = 1 if not self.is_truthy(value) else 0
            self.push(result)

        else:  # and, or
            if len(self.current_stack()) < 2:
                raise InterpreterError(f"Logical '{op}' requires two values")
            b = self.pop()
            a = self.pop()

            if op == "and":
                result = 1 if self.is_truthy(a) and self.is_truthy(b) else 0
            elif op == "or":
                result = 1 if self.is_truthy(a) or self.is_truthy(b) else 0
            else:
                raise InterpreterError(f"Unknown logical operation: {op}")

            self.push(result)

    def is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy."""
        if isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, (str, list)):
            return len(value) > 0
        elif value is None:
            return False
        else:
            return bool(value)

    def execute_control_flow(self, op: str) -> None:
        """Execute control flow operations."""
        if op == "if":
            if len(self.current_stack()) < 2:
                raise InterpreterError("If requires condition and code block")
            code_block = self.pop()
            condition = self.pop()

            if not isinstance(code_block, list):
                raise InterpreterError("If requires code block (list of statements)")

            if self.is_truthy(condition):
                for statement in code_block:
                    self.execute_statement(statement)

        elif op == "loop":
            if len(self.current_stack()) < 2:
                raise InterpreterError("Loop requires count and code block")
            code_block = self.pop()
            count = self.pop()

            if not isinstance(count, int) or count < 0:
                raise InterpreterError("Loop requires positive integer count")
            if not isinstance(code_block, list):
                raise InterpreterError("Loop requires code block (list of statements)")

            for _ in range(count):
                for statement in code_block:
                    self.execute_statement(statement)

        elif op == "when-stable":
            if not self.current_stack():
                raise InterpreterError("When-stable requires code block")
            code_block = self.pop()

            if not isinstance(code_block, list):
                raise InterpreterError("When-stable requires code block (list of statements)")

            if not self.timeline.has_paradoxes():
                for statement in code_block:
                    self.execute_statement(statement)

        else:
            raise InterpreterError(f"Unknown control flow: {op}")

    def execute_code_block(self, code_block: CodeBlockNode) -> None:
        """Execute a code block (push it as a list of statements)."""
        # Code blocks are pushed as executable lists onto the stack
        self.push(code_block.statements)

    def execute_word_definition(self, word_def: WordDefinitionNode) -> None:
        """Execute a word definition (store it for later use)."""
        self.words[word_def.name] = word_def.body

    def execute_word(self, word_name: str) -> None:
        """Execute a user-defined word."""
        if word_name not in self.words:
            raise InterpreterError(f"Unknown word: {word_name}")

        # Check for recursion
        if word_name in self.call_stack:
            raise InterpreterError(f"Recursive call detected: {word_name}")

        self.call_stack.append(word_name)
        try:
            word_body = self.words[word_name]
            for statement in word_body:
                self.execute_statement(statement)
        finally:
            self.call_stack.pop()

    def get_stack_display(self) -> str:
        """Get a string representation of the current stack."""
        stack = self.current_stack()
        if not stack:
            return "[]"

        items = []
        for item in stack:
            if isinstance(item, str):
                items.append(f'"{item}"')
            elif isinstance(item, list):
                items.append(f"[...{len(item)} items...]")
            else:
                items.append(str(item))

        return f"[{' '.join(items)}]"

    def get_state_info(self) -> Dict[str, Any]:
        """Get current interpreter state information."""
        timeline_info = self.timeline.get_timeline_info()

        return {
            "stack": self.current_stack(),
            "stack_size": len(self.current_stack()),
            "timeline_moment": timeline_info["current_moment"],
            "timeline_branch": timeline_info["current_branch"],
            "has_paradoxes": timeline_info["paradox_count"] > 0,
            "defined_words": list(self.words.keys()),
            "call_stack": self.call_stack.copy(),
        }
