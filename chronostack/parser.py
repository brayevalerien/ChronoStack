"""
Parser for ChronoStack - builds Abstract Syntax Tree from tokens.

The parser handles:
- Literals (numbers, strings, symbols)
- Operations (stack, temporal, math, comparison, logical, control flow)
- Code blocks [ ... ]
- Word definitions :name ... ;
"""

from dataclasses import dataclass
from typing import Any, List, Optional

from chronostack.lexer import Token, TokenType


@dataclass
class ASTNode:
    """Base class for AST nodes."""

    pass


@dataclass
class LiteralNode(ASTNode):
    """Literal value (number, string, symbol)."""

    value: Any
    token_type: TokenType


@dataclass
class OperationNode(ASTNode):
    """Operation (stack, temporal, math, comparison, logical, control flow)."""

    operation: str
    token_type: TokenType


@dataclass
class CodeBlockNode(ASTNode):
    """Code block [ ... ]."""

    statements: List[ASTNode]


@dataclass
class WordDefinitionNode(ASTNode):
    """Word definition :name ... ;"""

    name: str
    body: List[ASTNode]


@dataclass
class ProgramNode(ASTNode):
    """Root node containing all statements."""

    statements: List[ASTNode]


class ParseError(Exception):
    """Exception raised for parsing errors."""

    pass


class Parser:
    """Parser for ChronoStack language."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def error(self, message: str) -> None:
        """Raise a parser error with current token information."""
        token = self.current_token()
        raise ParseError(f"Parse error at line {token.line}, column {token.column}: {message}")

    def current_token(self) -> Token:
        """Get the current token."""
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.position]

    def peek_token(self, offset: int = 1) -> Token:
        """Look ahead at a token without consuming it."""
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[pos]

    def advance(self) -> Token:
        """Consume and return the current token."""
        token = self.current_token()
        if token.type != TokenType.EOF:
            self.position += 1
        return token

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token().type in token_types

    def consume(self, token_type: TokenType, message: str = None) -> Token:
        """Consume a token of the expected type or raise an error."""
        token = self.current_token()
        if token.type != token_type:
            if message:
                self.error(message)
            else:
                self.error(f"Expected {token_type.name}, got {token.type.name}")
        return self.advance()

    def skip_newlines(self) -> None:
        """Skip any newline tokens."""
        while self.match(TokenType.NEWLINE):
            self.advance()

    def parse_literal(self) -> LiteralNode:
        """Parse a literal value."""
        token = self.advance()

        if token.type == TokenType.NUMBER:
            return LiteralNode(int(token.value), token.type)
        elif token.type == TokenType.STRING or token.type == TokenType.SYMBOL:
            return LiteralNode(token.value, token.type)
        else:
            self.error(f"Expected literal, got {token.type.name}")

    def parse_code_block(self) -> CodeBlockNode:
        """Parse a code block [ ... ]."""
        self.consume(TokenType.LBRACKET, "Expected '['")
        statements = []

        self.skip_newlines()

        while not self.match(TokenType.RBRACKET, TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        self.consume(TokenType.RBRACKET, "Expected ']'")
        return CodeBlockNode(statements)

    def parse_word_definition(self) -> WordDefinitionNode:
        """Parse a word definition :name ... ;"""
        symbol_token = self.consume(TokenType.SYMBOL, "Expected symbol for word definition")
        name = symbol_token.value

        body = []
        self.skip_newlines()

        while not self.match(TokenType.SEMICOLON, TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue

            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        self.consume(TokenType.SEMICOLON, "Expected ';' to end word definition")
        return WordDefinitionNode(name, body)

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement."""
        self.skip_newlines()

        if self.match(TokenType.EOF):
            return None

        token = self.current_token()

        # Literals
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return self.parse_literal()

        # Code blocks
        elif self.match(TokenType.LBRACKET):
            return self.parse_code_block()

        # Word definitions (symbol at start of statement followed by content then semicolon)
        elif self.match(TokenType.SYMBOL):
            # Look ahead to see if this looks like a word definition
            # A word definition has the pattern: SYMBOL ... SEMICOLON
            if self.looks_like_word_definition():
                return self.parse_word_definition()
            else:
                # It's just a symbol literal
                return self.parse_literal()

        # Operations
        elif self.is_operation_token(token):
            op_token = self.advance()
            return OperationNode(op_token.value, op_token.type)

        else:
            self.error(f"Unexpected token: {token.type.name}")

    def is_operation_token(self, token: Token) -> bool:
        """Check if token represents an operation."""
        operation_types = {
            # Stack operations
            TokenType.PUSH,
            TokenType.POP,
            TokenType.DUP,
            TokenType.SWAP,
            TokenType.ROT,
            # Temporal operations
            TokenType.TICK,
            TokenType.REWIND,
            TokenType.PEEK_FUTURE,
            TokenType.BRANCH,
            TokenType.MERGE,
            TokenType.PARADOX,
            TokenType.ECHO,
            TokenType.SEND,
            TokenType.TEMPORAL_FOLD,
            TokenType.RIPPLE,
            # Math operations
            TokenType.ADD,
            TokenType.SUB,
            TokenType.MUL,
            TokenType.DIV,
            TokenType.MOD,
            # Comparison operations
            TokenType.LT,
            TokenType.GT,
            TokenType.EQ,
            # Logical operations
            TokenType.AND,
            TokenType.OR,
            TokenType.NOT,
            # Control flow
            TokenType.IF,
            TokenType.LOOP,
            TokenType.WHEN_STABLE,
        }
        return token.type in operation_types

    def looks_like_word_definition(self) -> bool:
        """Look ahead to determine if this symbol starts a word definition."""
        # Save current position
        saved_position = self.position

        # We're currently at a SYMBOL token, advance past it
        self.advance()

        # Look for content followed by a semicolon
        # Stop at EOF or when we encounter another symbol that could start a new definition
        found_content = False
        found_semicolon = False
        bracket_depth = 0

        while not self.match(TokenType.EOF):
            token = self.current_token()

            if self.match(TokenType.SEMICOLON) and bracket_depth == 0:
                found_semicolon = True
                break
            elif self.match(TokenType.LBRACKET):
                bracket_depth += 1
                found_content = True
            elif self.match(TokenType.RBRACKET):
                bracket_depth -= 1
                found_content = True
            elif self.match(TokenType.SYMBOL) and bracket_depth == 0:
                # If we encounter another symbol at top level, this might be a new statement
                # Only treat as word definition if we find the pattern symbol content ; symbol
                # We need to check if this symbol could be the start of another word definition
                break
            elif not self.match(TokenType.NEWLINE):
                found_content = True

            self.advance()

        # Restore position
        self.position = saved_position

        return found_content and found_semicolon

    def parse(self) -> ProgramNode:
        """Parse the entire program."""
        statements = []

        while not self.match(TokenType.EOF):
            self.skip_newlines()

            if self.match(TokenType.EOF):
                break

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        return ProgramNode(statements)
