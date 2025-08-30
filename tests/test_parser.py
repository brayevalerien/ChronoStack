"""Tests for the ChronoStack parser."""

import pytest

from chronostack.lexer import Lexer, TokenType
from chronostack.parser import (
    CodeBlockNode,
    LiteralNode,
    OperationNode,
    ParseError,
    Parser,
    ProgramNode,
    WordDefinitionNode,
)


class TestParser:
    """Test cases for the parser."""

    def parse_code(self, code: str) -> ProgramNode:
        """Helper to parse code string into AST."""
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_empty_program(self):
        """Test parsing empty program."""
        ast = self.parse_code("")
        assert isinstance(ast, ProgramNode)
        assert len(ast.statements) == 0

    def test_number_literal(self):
        """Test parsing number literals."""
        ast = self.parse_code("42 -17 0")
        assert len(ast.statements) == 3

        assert isinstance(ast.statements[0], LiteralNode)
        assert ast.statements[0].value == 42
        assert ast.statements[0].token_type == TokenType.NUMBER

        assert isinstance(ast.statements[1], LiteralNode)
        assert ast.statements[1].value == -17

        assert isinstance(ast.statements[2], LiteralNode)
        assert ast.statements[2].value == 0

    def test_string_literal(self):
        """Test parsing string literals."""
        ast = self.parse_code('"hello" "world"')
        assert len(ast.statements) == 2

        assert isinstance(ast.statements[0], LiteralNode)
        assert ast.statements[0].value == "hello"
        assert ast.statements[0].token_type == TokenType.STRING

        assert isinstance(ast.statements[1], LiteralNode)
        assert ast.statements[1].value == "world"

    def test_symbol_literal(self):
        """Test parsing symbol literals."""
        ast = self.parse_code(":foo :bar-baz")
        assert len(ast.statements) == 2

        assert isinstance(ast.statements[0], LiteralNode)
        assert ast.statements[0].value == ":foo"
        assert ast.statements[0].token_type == TokenType.SYMBOL

        assert isinstance(ast.statements[1], LiteralNode)
        assert ast.statements[1].value == ":bar-baz"

    def test_stack_operations(self):
        """Test parsing stack operations."""
        ast = self.parse_code("push pop dup swap rot")
        assert len(ast.statements) == 5

        expected_ops = ["push", "pop", "dup", "swap", "rot"]
        expected_types = [
            TokenType.PUSH,
            TokenType.POP,
            TokenType.DUP,
            TokenType.SWAP,
            TokenType.ROT,
        ]

        for i, (expected_op, expected_type) in enumerate(zip(expected_ops, expected_types)):
            assert isinstance(ast.statements[i], OperationNode)
            assert ast.statements[i].operation == expected_op
            assert ast.statements[i].token_type == expected_type

    def test_temporal_operations(self):
        """Test parsing temporal operations."""
        ast = self.parse_code("tick rewind peek-future branch merge paradox!")
        assert len(ast.statements) == 6

        expected_ops = ["tick", "rewind", "peek-future", "branch", "merge", "paradox!"]

        for i, expected_op in enumerate(expected_ops):
            assert isinstance(ast.statements[i], OperationNode)
            assert ast.statements[i].operation == expected_op

    def test_math_operations(self):
        """Test parsing math operations."""
        ast = self.parse_code("+ - * / %")
        assert len(ast.statements) == 5

        expected_ops = ["+", "-", "*", "/", "%"]
        expected_types = [TokenType.ADD, TokenType.SUB, TokenType.MUL, TokenType.DIV, TokenType.MOD]

        for i, (expected_op, expected_type) in enumerate(zip(expected_ops, expected_types)):
            assert isinstance(ast.statements[i], OperationNode)
            assert ast.statements[i].operation == expected_op
            assert ast.statements[i].token_type == expected_type

    def test_comparison_operations(self):
        """Test parsing comparison operations."""
        ast = self.parse_code("< > =")
        assert len(ast.statements) == 3

        expected_ops = ["<", ">", "="]
        expected_types = [TokenType.LT, TokenType.GT, TokenType.EQ]

        for i, (expected_op, expected_type) in enumerate(zip(expected_ops, expected_types)):
            assert isinstance(ast.statements[i], OperationNode)
            assert ast.statements[i].operation == expected_op
            assert ast.statements[i].token_type == expected_type

    def test_logical_operations(self):
        """Test parsing logical operations."""
        ast = self.parse_code("and or not")
        assert len(ast.statements) == 3

        expected_ops = ["and", "or", "not"]
        expected_types = [TokenType.AND, TokenType.OR, TokenType.NOT]

        for i, (expected_op, expected_type) in enumerate(zip(expected_ops, expected_types)):
            assert isinstance(ast.statements[i], OperationNode)
            assert ast.statements[i].operation == expected_op
            assert ast.statements[i].token_type == expected_type

    def test_control_flow_operations(self):
        """Test parsing control flow operations."""
        ast = self.parse_code("if loop when-stable")
        assert len(ast.statements) == 3

        expected_ops = ["if", "loop", "when-stable"]
        expected_types = [TokenType.IF, TokenType.LOOP, TokenType.WHEN_STABLE]

        for i, (expected_op, expected_type) in enumerate(zip(expected_ops, expected_types)):
            assert isinstance(ast.statements[i], OperationNode)
            assert ast.statements[i].operation == expected_op
            assert ast.statements[i].token_type == expected_type

    def test_simple_code_block(self):
        """Test parsing simple code blocks."""
        ast = self.parse_code("[ 42 dup + ]")
        assert len(ast.statements) == 1

        block = ast.statements[0]
        assert isinstance(block, CodeBlockNode)
        assert len(block.statements) == 3

        assert isinstance(block.statements[0], LiteralNode)
        assert block.statements[0].value == 42

        assert isinstance(block.statements[1], OperationNode)
        assert block.statements[1].operation == "dup"

        assert isinstance(block.statements[2], OperationNode)
        assert block.statements[2].operation == "+"

    def test_empty_code_block(self):
        """Test parsing empty code blocks."""
        ast = self.parse_code("[ ]")
        assert len(ast.statements) == 1

        block = ast.statements[0]
        assert isinstance(block, CodeBlockNode)
        assert len(block.statements) == 0

    def test_nested_code_blocks(self):
        """Test parsing nested code blocks."""
        ast = self.parse_code("[ 42 [ dup + ] swap ]")
        assert len(ast.statements) == 1

        outer_block = ast.statements[0]
        assert isinstance(outer_block, CodeBlockNode)
        assert len(outer_block.statements) == 3

        # Check inner block
        inner_block = outer_block.statements[1]
        assert isinstance(inner_block, CodeBlockNode)
        assert len(inner_block.statements) == 2

    def test_simple_word_definition(self):
        """Test parsing simple word definitions."""
        ast = self.parse_code(":double dup + ;")
        assert len(ast.statements) == 1

        word_def = ast.statements[0]
        assert isinstance(word_def, WordDefinitionNode)
        assert word_def.name == "double"
        assert len(word_def.body) == 2

        assert isinstance(word_def.body[0], OperationNode)
        assert word_def.body[0].operation == "dup"

        assert isinstance(word_def.body[1], OperationNode)
        assert word_def.body[1].operation == "+"

    def test_word_definition_with_code_block(self):
        """Test parsing word definitions with code blocks."""
        ast = self.parse_code(":conditional dup 0 > if [ 2 * ] [ pop 0 ] ;")
        assert len(ast.statements) == 1

        word_def = ast.statements[0]
        assert isinstance(word_def, WordDefinitionNode)
        assert word_def.name == "conditional"

        # Should contain: dup, 0, >, if, [2 *], [pop 0]
        assert len(word_def.body) == 6

        # Check the code blocks
        true_block = word_def.body[4]
        false_block = word_def.body[5]

        assert isinstance(true_block, CodeBlockNode)
        assert isinstance(false_block, CodeBlockNode)

    def test_mixed_statements(self):
        """Test parsing mixed statement types."""
        ast = self.parse_code("""
        42 "hello" :symbol
        [ dup + ]
        :square dup * ;
        tick
        """)

        assert len(ast.statements) == 6

        # Literals
        assert isinstance(ast.statements[0], LiteralNode)
        assert ast.statements[0].value == 42

        assert isinstance(ast.statements[1], LiteralNode)
        assert ast.statements[1].value == "hello"

        assert isinstance(ast.statements[2], LiteralNode)
        assert ast.statements[2].value == ":symbol"

        # Code block
        assert isinstance(ast.statements[3], CodeBlockNode)

        # Word definition
        assert isinstance(ast.statements[4], WordDefinitionNode)
        assert ast.statements[4].name == "square"

        # Operation
        assert isinstance(ast.statements[5], OperationNode)
        assert ast.statements[5].operation == "tick"

    def test_comments_ignored(self):
        """Test that comments are ignored in parsing."""
        ast = self.parse_code("""
        42 # this is a number
        # this is a comment line
        "hello" # string literal
        """)

        assert len(ast.statements) == 2
        assert isinstance(ast.statements[0], LiteralNode)
        assert ast.statements[0].value == 42
        assert isinstance(ast.statements[1], LiteralNode)
        assert ast.statements[1].value == "hello"

    def test_unterminated_code_block_error(self):
        """Test error handling for unterminated code blocks."""
        with pytest.raises(ParseError, match="Expected ']'"):
            self.parse_code("[ 42 dup")

    def test_unterminated_word_definition_not_parsed_as_definition(self):
        """Test that unterminated word definitions are parsed as separate tokens."""
        ast = self.parse_code(":double dup +")
        # Should be parsed as 3 separate statements, not a word definition
        assert len(ast.statements) == 3
        assert isinstance(ast.statements[0], LiteralNode)
        assert ast.statements[0].value == ":double"
        assert isinstance(ast.statements[1], OperationNode)
        assert ast.statements[1].operation == "dup"
        assert isinstance(ast.statements[2], OperationNode)
        assert ast.statements[2].operation == "+"

    def test_complex_fibonacci_program(self):
        """Test parsing a complex fibonacci program."""
        program = """
        # Fibonacci using temporal mechanics
        :fib
            dup 2 < if [ pop 1 ] [
                dup 1 - echo 2 - echo +
            ] ;

        5 fib
        """

        ast = self.parse_code(program)

        # Should have word definition and then "5 fib"
        assert len(ast.statements) == 3  # :fib definition, 5, fib

        # Check word definition structure
        word_def = ast.statements[0]
        assert isinstance(word_def, WordDefinitionNode)
        assert word_def.name == "fib"

        # Should contain the if-then-else structure
        assert len(word_def.body) >= 3  # At minimum: dup, condition, if, blocks

    def test_whitespace_and_newlines(self):
        """Test that whitespace and newlines are handled correctly."""
        ast = self.parse_code("""

        42

        dup

        +

        """)

        assert len(ast.statements) == 3
        assert isinstance(ast.statements[0], LiteralNode)
        assert isinstance(ast.statements[1], OperationNode)
        assert isinstance(ast.statements[2], OperationNode)

    def test_parser_edge_cases(self):
        """Test parser edge cases for coverage."""
        from chronostack.lexer import Token, TokenType

        # Test peek_token with offset beyond bounds
        parser = Parser([Token(TokenType.NUMBER, "42", 1, 1), Token(TokenType.EOF, "", 1, 3)])

        # Should handle offset beyond bounds gracefully
        peek_token = parser.peek_token(5)  # Way beyond bounds
        assert peek_token.type == TokenType.EOF

        # Test current_token at end
        parser.position = 99  # Beyond end
        current = parser.current_token()
        assert current.type == TokenType.EOF

    def test_parser_error_handling(self):
        """Test various parser error conditions."""
        import pytest

        from chronostack.lexer import Token, TokenType
        from chronostack.parser import ParseError

        # Test consume with wrong token type
        parser = Parser([Token(TokenType.NUMBER, "42", 1, 1), Token(TokenType.EOF, "", 1, 3)])
        with pytest.raises(ParseError, match="Expected"):
            parser.consume(TokenType.STRING, "Expected string")

        # Test error method
        parser = Parser([Token(TokenType.NUMBER, "42", 1, 1), Token(TokenType.EOF, "", 1, 3)])
        with pytest.raises(ParseError, match="Test error"):
            parser.error("Test error")
