from typing import Optional, Union
from sintactico import (
    ASTNode, ProgramNode, VarDeclarationNode, AssignmentNode,
    BinaryOpNode, UnaryOpNode, NumberNode, IdentifierNode,
    IfNode, WhileNode, PrintNode
)
from tabla_simbolos import SymbolTable, SymbolType


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []

    def analyze(self, ast: ASTNode) -> SymbolTable:
        self.errors = []
        self.warnings = []

        try:
            self.visit(ast)
            self.warnings.extend(self.symbol_table.get_warnings())

            if self.errors:
                error_msg = "\n".join(self.errors)
                raise SemanticError(f"Se encontraron errores semanticos:\n{error_msg}")

            return self.symbol_table

        except SemanticError:
            raise
        except Exception as e:
            raise SemanticError(f"Error durante el analisis semantico: {str(e)}")

    def visit(self, node: ASTNode):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        raise Exception(f"No existe metodo visit_{type(node).__name__}")

    def visit_ProgramNode(self, node: ProgramNode):
        for statement in node.statements:
            self.visit(statement)

    def visit_VarDeclarationNode(self, node: VarDeclarationNode):
        try:
            self.symbol_table.declare(
                name=node.identifier,
                symbol_type=SymbolType.VARIABLE,
                line=node.line
            )
        except Exception as e:
            self.errors.append(str(e))

    def visit_AssignmentNode(self, node: AssignmentNode):
        if not self.symbol_table.exists(node.identifier):
            self.errors.append(
                f"Error semantico (linea {node.line}): "
                f"Variable '{node.identifier}' no declarada."
            )
            return

        expr_type = self.visit(node.expression)
        self.symbol_table.mark_as_initialized(node.identifier)
        return expr_type

    def visit_BinaryOpNode(self, node: BinaryOpNode):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if node.operator in ['+', '-', '*', '/']:
            if left_type in ['int', 'float', None] and right_type in ['int', 'float', None]:
                if left_type == 'float' or right_type == 'float':
                    return 'float'
                return 'int'
            else:
                self.errors.append(
                    f"Error semantico (linea {node.line}): "
                    f"Operador '{node.operator}' requiere operandos numericos."
                )
                return None

        elif node.operator in ['==', '!=', '<', '>', '<=', '>=']:
            if left_type in ['int', 'float', None] and right_type in ['int', 'float', None]:
                return 'bool'
            else:
                self.errors.append(
                    f"Error semantico (linea {node.line}): "
                    f"Operador '{node.operator}' requiere operandos comparables."
                )
                return None

        return None

    def visit_UnaryOpNode(self, node: UnaryOpNode):
        operand_type = self.visit(node.operand)

        if node.operator in ['+', '-']:
            if operand_type in ['int', 'float', None]:
                return operand_type
            else:
                self.errors.append(
                    f"Error semantico (linea {node.line}): "
                    f"Operador unario '{node.operator}' requiere operando numerico."
                )
                return None

        return None

    def visit_NumberNode(self, node: NumberNode):
        if isinstance(node.value, int):
            return 'int'
        elif isinstance(node.value, float):
            return 'float'
        return None

    def visit_IdentifierNode(self, node: IdentifierNode):
        if not self.symbol_table.exists(node.name):
            self.errors.append(
                f"Error semantico (linea {node.line}): "
                f"Variable '{node.name}' no declarada."
            )
            return None

        self.symbol_table.mark_as_used(node.name)
        symbol = self.symbol_table.lookup(node.name)

        if not symbol.initialized:
            self.warnings.append(
                f"Advertencia (linea {node.line}): "
                f"Variable '{node.name}' podria no estar inicializada."
            )

        return symbol.data_type

    def visit_IfNode(self, node: IfNode):
        self.visit(node.condition)

        for stmt in node.then_block:
            self.visit(stmt)

        if node.else_block:
            for stmt in node.else_block:
                self.visit(stmt)

    def visit_WhileNode(self, node: WhileNode):
        self.visit(node.condition)

        for stmt in node.body:
            self.visit(stmt)

    def visit_PrintNode(self, node: PrintNode):
        self.visit(node.expression)

    def print_results(self):
        print("\n" + "="*80)
        print("ANALISIS SEMANTICO")
        print("="*80)

        if self.errors:
            print("\nERRORES ENCONTRADOS:")
            print("-"*80)
            for error in self.errors:
                print(f"  {error}")
            print("="*80 + "\n")
        else:
            print("\nNo se encontraron errores semanticos.")
            print("="*80 + "\n")

        if self.warnings:
            print("ADVERTENCIAS:")
            print("-"*80)
            for warning in self.warnings:
                print(f"  {warning}")
            print("="*80 + "\n")


if __name__ == "__main__":
    from lexico import Lexer
    from sintactico import Parser

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

    analyzer = SemanticAnalyzer()
    symbol_table = analyzer.analyze(ast)

    analyzer.print_results()
    symbol_table.print_table()
