from dataclasses import dataclass
from typing import List, Optional, Union
from lexico import Token, TokenType, Lexer


@dataclass
class ASTNode:
    pass


@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode]


@dataclass
class VarDeclarationNode(ASTNode):
    identifier: str
    line: int


@dataclass
class AssignmentNode(ASTNode):
    identifier: str
    expression: ASTNode
    line: int


@dataclass
class BinaryOpNode(ASTNode):
    operator: str
    left: ASTNode
    right: ASTNode
    line: int


@dataclass
class UnaryOpNode(ASTNode):
    operator: str
    operand: ASTNode
    line: int


@dataclass
class NumberNode(ASTNode):
    value: Union[int, float]
    line: int


@dataclass
class IdentifierNode(ASTNode):
    name: str
    line: int


@dataclass
class IfNode(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]]
    line: int


@dataclass
class WhileNode(ASTNode):
    condition: ASTNode
    body: List[ASTNode]
    line: int


@dataclass
class PrintNode(ASTNode):
    expression: ASTNode
    line: int


class SyntaxError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None

    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def expect(self, token_type: TokenType) -> Token:
        if self.current_token is None:
            raise SyntaxError(f"Se esperaba {token_type.name} pero se llego al final del archivo")

        if self.current_token.type != token_type:
            raise SyntaxError(
                f"Se esperaba {token_type.name} pero se encontro {self.current_token.type.name} "
                f"en linea {self.current_token.line}, columna {self.current_token.column}"
            )

        token = self.current_token
        self.advance()
        return token

    def parse(self) -> ProgramNode:
        statements = []

        while self.current_token and self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        return ProgramNode(statements)

    def parse_statement(self) -> Optional[ASTNode]:
        if self.current_token.type == TokenType.VAR:
            return self.parse_var_declaration()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif self.current_token.type == TokenType.PRINT:
            return self.parse_print_statement()
        elif self.current_token.type == TokenType.IDENTIFIER:
            return self.parse_assignment()
        else:
            raise SyntaxError(
                f"Sentencia no esperada: {self.current_token.type.name} "
                f"en linea {self.current_token.line}"
            )

    def parse_var_declaration(self) -> VarDeclarationNode:
        line = self.current_token.line
        self.expect(TokenType.VAR)
        identifier_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.SEMICOLON)

        return VarDeclarationNode(identifier_token.value, line)

    def parse_assignment(self) -> AssignmentNode:
        line = self.current_token.line
        identifier_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        expression = self.parse_expression()
        self.expect(TokenType.SEMICOLON)

        return AssignmentNode(identifier_token.value, expression, line)

    def parse_if_statement(self) -> IfNode:
        line = self.current_token.line
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)

        then_block = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)

        self.expect(TokenType.RBRACE)

        else_block = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.LBRACE)

            else_block = []
            while self.current_token and self.current_token.type != TokenType.RBRACE:
                stmt = self.parse_statement()
                if stmt:
                    else_block.append(stmt)

            self.expect(TokenType.RBRACE)

        return IfNode(condition, then_block, else_block, line)

    def parse_while_statement(self) -> WhileNode:
        line = self.current_token.line
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)

        body = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)

        self.expect(TokenType.RBRACE)

        return WhileNode(condition, body, line)

    def parse_print_statement(self) -> PrintNode:
        line = self.current_token.line
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        expression = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)

        return PrintNode(expression, line)

    def parse_expression(self) -> ASTNode:
        return self.parse_comparison()

    def parse_comparison(self) -> ASTNode:
        node = self.parse_term()

        while self.current_token and self.current_token.type in [
            TokenType.LESS_THAN, TokenType.GREATER_THAN,
            TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
            TokenType.EQUAL, TokenType.NOT_EQUAL
        ]:
            op_token = self.current_token
            self.advance()
            right = self.parse_term()
            node = BinaryOpNode(op_token.value, node, right, op_token.line)

        return node

    def parse_term(self) -> ASTNode:
        node = self.parse_factor()

        while self.current_token and self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            op_token = self.current_token
            self.advance()
            right = self.parse_factor()
            node = BinaryOpNode(op_token.value, node, right, op_token.line)

        return node

    def parse_factor(self) -> ASTNode:
        node = self.parse_unary()

        while self.current_token and self.current_token.type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            op_token = self.current_token
            self.advance()
            right = self.parse_unary()
            node = BinaryOpNode(op_token.value, node, right, op_token.line)

        return node

    def parse_unary(self) -> ASTNode:
        if self.current_token and self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            op_token = self.current_token
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(op_token.value, operand, op_token.line)

        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        if self.current_token.type == TokenType.NUMBER:
            token = self.current_token
            self.advance()
            return NumberNode(token.value, token.line)

        elif self.current_token.type == TokenType.IDENTIFIER:
            token = self.current_token
            self.advance()
            return IdentifierNode(token.value, token.line)

        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            node = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return node

        else:
            raise SyntaxError(
                f"Token inesperado: {self.current_token.type.name} "
                f"en linea {self.current_token.line}"
            )

    def print_ast(self, node: ASTNode, indent: int = 0):
        prefix = "  " * indent

        if isinstance(node, ProgramNode):
            print(f"{prefix}Programa:")
            for stmt in node.statements:
                self.print_ast(stmt, indent + 1)

        elif isinstance(node, VarDeclarationNode):
            print(f"{prefix}Declaracion de Variable: '{node.identifier}' (linea {node.line})")

        elif isinstance(node, AssignmentNode):
            print(f"{prefix}Asignacion: '{node.identifier}' = (linea {node.line})")
            self.print_ast(node.expression, indent + 1)

        elif isinstance(node, BinaryOpNode):
            print(f"{prefix}Operacion Binaria: '{node.operator}' (linea {node.line})")
            self.print_ast(node.left, indent + 1)
            self.print_ast(node.right, indent + 1)

        elif isinstance(node, UnaryOpNode):
            print(f"{prefix}Operacion Unaria: '{node.operator}' (linea {node.line})")
            self.print_ast(node.operand, indent + 1)

        elif isinstance(node, NumberNode):
            print(f"{prefix}Numero: {node.value} (linea {node.line})")

        elif isinstance(node, IdentifierNode):
            print(f"{prefix}Identificador: '{node.name}' (linea {node.line})")

        elif isinstance(node, IfNode):
            print(f"{prefix}If (linea {node.line}):")
            print(f"{prefix}  Condicion:")
            self.print_ast(node.condition, indent + 2)
            print(f"{prefix}  Then:")
            for stmt in node.then_block:
                self.print_ast(stmt, indent + 2)
            if node.else_block:
                print(f"{prefix}  Else:")
                for stmt in node.else_block:
                    self.print_ast(stmt, indent + 2)

        elif isinstance(node, WhileNode):
            print(f"{prefix}While (linea {node.line}):")
            print(f"{prefix}  Condicion:")
            self.print_ast(node.condition, indent + 2)
            print(f"{prefix}  Cuerpo:")
            for stmt in node.body:
                self.print_ast(stmt, indent + 2)

        elif isinstance(node, PrintNode):
            print(f"{prefix}Print (linea {node.line}):")
            self.print_ast(node.expression, indent + 1)


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

    print("Codigo fuente:")
    print(codigo)

    lexer = Lexer(codigo)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    print("\n" + "="*60)
    print("ANALISIS SINTACTICO - ARBOL DE SINTAXIS ABSTRACTA (AST)")
    print("="*60 + "\n")
    parser.print_ast(ast)
