import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    VAR = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    PRINT = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    ASSIGN = auto()
    SEMICOLON = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class LexicalError(Exception):
    pass


class Lexer:
    KEYWORDS = {
        'var': TokenType.VAR,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'print': TokenType.PRINT,
    }

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def current_char(self) -> Optional[str]:
        if self.position >= len(self.source_code):
            return None
        return self.source_code[self.position]

    def peek_char(self, offset: int = 1) -> Optional[str]:
        pos = self.position + offset
        if pos >= len(self.source_code):
            return None
        return self.source_code[pos]

    def advance(self):
        if self.position < len(self.source_code):
            if self.source_code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()

    def skip_comment(self):
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()

    def read_number(self) -> Token:
        start_line = self.line
        start_column = self.column
        num_str = ''

        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            num_str += self.current_char()
            self.advance()

        if '.' in num_str:
            value = float(num_str)
        else:
            value = int(num_str)

        return Token(TokenType.NUMBER, value, start_line, start_column)

    def read_identifier(self) -> Token:
        start_line = self.line
        start_column = self.column
        id_str = ''

        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            id_str += self.current_char()
            self.advance()

        token_type = self.KEYWORDS.get(id_str, TokenType.IDENTIFIER)
        return Token(token_type, id_str, start_line, start_column)

    def tokenize(self) -> List[Token]:
        self.tokens = []

        while self.current_char() is not None:
            if self.current_char() in ' \t\r':
                self.skip_whitespace()
                continue

            if self.current_char() == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue

            if self.current_char() == '\n':
                self.advance()
                continue

            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue

            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue

            char = self.current_char()
            next_char = self.peek_char()
            line = self.line
            column = self.column

            if char == '=' and next_char == '=':
                self.tokens.append(Token(TokenType.EQUAL, '==', line, column))
                self.advance()
                self.advance()
                continue

            if char == '!' and next_char == '=':
                self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', line, column))
                self.advance()
                self.advance()
                continue

            if char == '<' and next_char == '=':
                self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', line, column))
                self.advance()
                self.advance()
                continue

            if char == '>' and next_char == '=':
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', line, column))
                self.advance()
                self.advance()
                continue

            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '=': TokenType.ASSIGN,
                ';': TokenType.SEMICOLON,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '<': TokenType.LESS_THAN,
                '>': TokenType.GREATER_THAN,
            }

            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, line, column))
                self.advance()
                continue

            raise LexicalError(f"Caracter no reconocido '{char}' en linea {line}, columna {column}")

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def print_tokens(self):
        print("\n" + "="*60)
        print("ANALISIS LEXICO - TABLA DE TOKENS")
        print("="*60)
        print(f"{'Tipo':<20} {'Valor':<15} {'Linea':<10} {'Columna':<10}")
        print("-"*60)

        for token in self.tokens:
            if token.type != TokenType.EOF:
                print(f"{token.type.name:<20} {str(token.value):<15} {token.line:<10} {token.column:<10}")

        print("="*60)
        print(f"Total de tokens: {len(self.tokens) - 1}")
        print("="*60 + "\n")


if __name__ == "__main__":
    codigo = """
    var x;
    var y;
    x = 10;
    y = 20;
    var suma;
    suma = x + y;
    print(suma);
    """

    lexer = Lexer(codigo)
    tokens = lexer.tokenize()
    lexer.print_tokens()
