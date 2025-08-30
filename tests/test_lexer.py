"""Tests for the ChronoStack lexer."""

import pytest

from chronostack.lexer import Lexer, TokenType


class TestLexer:
    """Test cases for the lexer."""

    def test_empty_input(self):
        """Test lexing empty input."""
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_numbers(self):
        """Test lexing integer numbers."""
        lexer = Lexer("42 -17 0")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "42"

        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == "-17"

        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == "0"

    def test_strings(self):
        """Test lexing double-quoted strings."""
        lexer = Lexer('"hello" "world with spaces" "escape\\ntest"')
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

        assert tokens[1].type == TokenType.STRING
        assert tokens[1].value == "world with spaces"

        assert tokens[2].type == TokenType.STRING
        assert tokens[2].value == "escape\ntest"

    def test_symbols(self):
        """Test lexing symbols."""
        lexer = Lexer(":foo :bar-baz :test_123")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.SYMBOL
        assert tokens[0].value == ":foo"

        assert tokens[1].type == TokenType.SYMBOL
        assert tokens[1].value == ":bar-baz"

        assert tokens[2].type == TokenType.SYMBOL
        assert tokens[2].value == ":test_123"

    def test_stack_operations(self):
        """Test lexing stack operation keywords."""
        lexer = Lexer("push pop dup swap rot")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.PUSH,
            TokenType.POP,
            TokenType.DUP,
            TokenType.SWAP,
            TokenType.ROT,
        ]

        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_temporal_operations(self):
        """Test lexing temporal operation keywords."""
        lexer = Lexer("tick rewind peek-future branch merge paradox! echo send")
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.TICK,
            TokenType.REWIND,
            TokenType.PEEK_FUTURE,
            TokenType.BRANCH,
            TokenType.MERGE,
            TokenType.PARADOX,
            TokenType.ECHO,
            TokenType.SEND,
        ]

        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_math_operations(self):
        """Test lexing math operation symbols."""
        lexer = Lexer("+ - * / %")
        tokens = lexer.tokenize()

        expected_types = [TokenType.ADD, TokenType.SUB, TokenType.MUL, TokenType.DIV, TokenType.MOD]

        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_comparison_operations(self):
        """Test lexing comparison operations."""
        lexer = Lexer("< > =")
        tokens = lexer.tokenize()

        expected_types = [TokenType.LT, TokenType.GT, TokenType.EQ]

        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_logical_operations(self):
        """Test lexing logical operations."""
        lexer = Lexer("and or not")
        tokens = lexer.tokenize()

        expected_types = [TokenType.AND, TokenType.OR, TokenType.NOT]

        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_control_flow(self):
        """Test lexing control flow keywords."""
        lexer = Lexer("if loop when-stable")
        tokens = lexer.tokenize()

        expected_types = [TokenType.IF, TokenType.LOOP, TokenType.WHEN_STABLE]

        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type

    def test_brackets_and_semicolon(self):
        """Test lexing brackets and semicolon."""
        lexer = Lexer("[ ] ;")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET
        assert tokens[2].type == TokenType.SEMICOLON

    def test_comments(self):
        """Test that comments are skipped."""
        lexer = Lexer("42 # this is a comment\n17")
        tokens = lexer.tokenize()

        # Should have: NUMBER, NEWLINE, NUMBER, EOF
        assert len(tokens) == 4
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "42"
        assert tokens[1].type == TokenType.NEWLINE
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == "17"

    def test_word_definition(self):
        """Test lexing word definition syntax."""
        lexer = Lexer(":double dup + ;")
        tokens = lexer.tokenize()

        expected = [
            (TokenType.SYMBOL, ":double"),
            (TokenType.DUP, "dup"),
            (TokenType.ADD, "+"),
            (TokenType.SEMICOLON, ";"),
        ]

        for i, (expected_type, expected_value) in enumerate(expected):
            assert tokens[i].type == expected_type
            assert tokens[i].value == expected_value

    def test_code_block(self):
        """Test lexing code blocks."""
        lexer = Lexer("[ 42 dup + ]")
        tokens = lexer.tokenize()

        expected = [
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.DUP,
            TokenType.ADD,
            TokenType.RBRACKET,
        ]

        for i, expected_type in enumerate(expected):
            assert tokens[i].type == expected_type

    def test_line_and_column_tracking(self):
        """Test that line and column numbers are tracked correctly."""
        lexer = Lexer("42\n  17")
        tokens = lexer.tokenize()

        # First token should be at line 1, column 1
        assert tokens[0].line == 1
        assert tokens[0].column == 1

        # Newline should be at line 1, column 3
        assert tokens[1].line == 1
        assert tokens[1].column == 3

        # Second number should be at line 2, column 3
        assert tokens[2].line == 2
        assert tokens[2].column == 3

    def test_unterminated_string_error(self):
        """Test error handling for unterminated strings."""
        lexer = Lexer('"unterminated')
        with pytest.raises(ValueError, match="Unterminated string"):
            lexer.tokenize()

    def test_invalid_character_error(self):
        """Test error handling for invalid characters."""
        lexer = Lexer("@")
        with pytest.raises(ValueError, match="Unexpected character"):
            lexer.tokenize()

    def test_complex_program(self):
        """Test lexing a complex ChronoStack program."""
        program = """
        # Fibonacci using temporal mechanics
        :fib
            dup 2 < if [ pop 1 ] [
                dup 1 - echo 2 - echo +
            ] ;

        5 fib
        """

        lexer = Lexer(program)
        tokens = lexer.tokenize()

        # Just verify it doesn't crash and produces reasonable tokens
        assert len(tokens) > 10
        assert tokens[-1].type == TokenType.EOF

        # Check some key tokens are present
        token_types = [token.type for token in tokens]
        assert TokenType.SYMBOL in token_types
        assert TokenType.DUP in token_types
        assert TokenType.IF in token_types
        assert TokenType.ECHO in token_types
