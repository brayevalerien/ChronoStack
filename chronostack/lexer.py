"""
Lexer for ChronoStack - tokenizes the temporal stack-based language.

Tokens:
- Numbers: integers
- Strings: double-quoted
- Symbols: :identifier
- Operators: stack, temporal, math, comparison, logical, control flow
- Brackets: [ ] for code blocks
- Semicolon: ; for definition end
- Comments: # to end of line
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    SYMBOL = auto()

    # Stack operations
    PUSH = auto()
    POP = auto()
    DUP = auto()
    SWAP = auto()
    ROT = auto()

    # Temporal operations
    TICK = auto()
    REWIND = auto()
    PEEK_FUTURE = auto()
    BRANCH = auto()
    MERGE = auto()
    PARADOX = auto()
    ECHO = auto()
    SEND = auto()
    TEMPORAL_FOLD = auto()
    RIPPLE = auto()

    # Math operations
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()

    # Comparison operations
    LT = auto()
    GT = auto()
    EQ = auto()

    # Logical operations
    AND = auto()
    OR = auto()
    NOT = auto()

    # Control flow
    IF = auto()
    LOOP = auto()
    WHEN_STABLE = auto()

    # Structure
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()

    # Special
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    """Tokenizer for ChronoStack language."""

    # Keyword mapping
    KEYWORDS = {
        "push": TokenType.PUSH,
        "pop": TokenType.POP,
        "dup": TokenType.DUP,
        "swap": TokenType.SWAP,
        "rot": TokenType.ROT,
        "tick": TokenType.TICK,
        "rewind": TokenType.REWIND,
        "peek-future": TokenType.PEEK_FUTURE,
        "branch": TokenType.BRANCH,
        "merge": TokenType.MERGE,
        "paradox!": TokenType.PARADOX,
        "echo": TokenType.ECHO,
        "send": TokenType.SEND,
        "temporal-fold": TokenType.TEMPORAL_FOLD,
        "ripple": TokenType.RIPPLE,
        "+": TokenType.ADD,
        "-": TokenType.SUB,
        "*": TokenType.MUL,
        "/": TokenType.DIV,
        "%": TokenType.MOD,
        "<": TokenType.LT,
        ">": TokenType.GT,
        "=": TokenType.EQ,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
        "if": TokenType.IF,
        "loop": TokenType.LOOP,
        "when-stable": TokenType.WHEN_STABLE,
    }

    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1

    def error(self, message: str) -> None:
        """Raise a lexer error with position information."""
        raise ValueError(f"Lexer error at line {self.line}, column {self.column}: {message}")

    def peek(self, offset: int = 0) -> Optional[str]:
        """Look ahead at character without consuming it."""
        pos = self.position + offset
        if pos >= len(self.text):
            return None
        return self.text[pos]

    def advance(self) -> Optional[str]:
        """Consume and return the current character."""
        if self.position >= len(self.text):
            return None

        char = self.text[self.position]
        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self) -> None:
        """Skip whitespace characters except newlines."""
        while self.peek() and self.peek() in " \t\r":
            self.advance()

    def skip_comment(self) -> None:
        """Skip comment from # to end of line."""
        while self.peek() and self.peek() != "\n":
            self.advance()

    def read_number(self) -> Token:
        """Read an integer number."""
        start_line, start_col = self.line, self.column
        value = ""

        # Handle negative numbers
        if self.peek() == "-":
            value += self.advance()

        while self.peek() and self.peek().isdigit():
            value += self.advance()

        if not value or value == "-":
            self.error("Invalid number")

        return Token(TokenType.NUMBER, value, start_line, start_col)

    def read_string(self) -> Token:
        """Read a double-quoted string."""
        start_line, start_col = self.line, self.column
        self.advance()  # Skip opening quote
        value = ""

        while self.peek() and self.peek() != '"':
            char = self.advance()
            if char == "\\":
                # Handle escape sequences
                next_char = self.advance()
                if next_char == "n":
                    value += "\n"
                elif next_char == "t":
                    value += "\t"
                elif next_char == "r":
                    value += "\r"
                elif next_char == "\\":
                    value += "\\"
                elif next_char == '"':
                    value += '"'
                else:
                    value += next_char
            else:
                value += char

        if not self.peek():
            self.error("Unterminated string")

        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, value, start_line, start_col)

    def read_symbol(self) -> Token:
        """Read a symbol starting with colon."""
        start_line, start_col = self.line, self.column
        self.advance()  # Skip colon

        if not self.peek() or not (self.peek().isalpha() or self.peek() == "_"):
            self.error("Invalid symbol")

        value = ":"
        while self.peek() and (self.peek().isalnum() or self.peek() in "_-"):
            value += self.advance()

        return Token(TokenType.SYMBOL, value, start_line, start_col)

    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_line, start_col = self.line, self.column
        value = ""

        # First character
        if self.peek():
            value += self.advance()

        # Continue reading if it's part of a multi-character identifier
        while self.peek() and (self.peek().isalnum() or self.peek() in "_-!"):
            value += self.advance()

        token_type = self.KEYWORDS.get(value, TokenType.SYMBOL)
        return Token(token_type, value, start_line, start_col)

    def tokenize(self) -> List[Token]:
        """Tokenize the entire input text."""
        tokens = []

        while self.position < len(self.text):
            self.skip_whitespace()

            if not self.peek():
                break

            char = self.peek()

            if char == "\n":
                tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.column))
                self.advance()
            elif char == "#":
                self.skip_comment()
            elif char.isdigit() or (char == "-" and self.peek(1) and self.peek(1).isdigit()):
                tokens.append(self.read_number())
            elif char == '"':
                tokens.append(self.read_string())
            elif char == ":":
                tokens.append(self.read_symbol())
            elif char == "[":
                tokens.append(Token(TokenType.LBRACKET, "[", self.line, self.column))
                self.advance()
            elif char == "]":
                tokens.append(Token(TokenType.RBRACKET, "]", self.line, self.column))
                self.advance()
            elif char == ";":
                tokens.append(Token(TokenType.SEMICOLON, ";", self.line, self.column))
                self.advance()
            elif char in "+-*/%<>=" or char.isalpha() or char == "_":
                tokens.append(self.read_identifier())
            else:
                self.error(f"Unexpected character: {char}")

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens
