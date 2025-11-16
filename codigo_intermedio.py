from dataclasses import dataclass
from typing import List, Optional, Union
from sintactico import (
    ASTNode, ProgramNode, VarDeclarationNode, AssignmentNode,
    BinaryOpNode, UnaryOpNode, NumberNode, IdentifierNode,
    IfNode, WhileNode, PrintNode
)


@dataclass
class ThreeAddressCode:
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    result: Optional[str] = None

    def __str__(self):
        if self.op == 'ASSIGN':
            return f"{self.result} = {self.arg1}"
        elif self.op == 'LABEL':
            return f"{self.result}:"
        elif self.op == 'GOTO':
            return f"goto {self.result}"
        elif self.op == 'IF_FALSE':
            return f"if_false {self.arg1} goto {self.result}"
        elif self.op == 'IF_TRUE':
            return f"if_true {self.arg1} goto {self.result}"
        elif self.op == 'PRINT':
            return f"print {self.arg1}"
        elif self.op in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=']:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op == 'UNARY_MINUS':
            return f"{self.result} = -{self.arg1}"
        elif self.op == 'UNARY_PLUS':
            return f"{self.result} = +{self.arg1}"
        else:
            return f"{self.op} {self.arg1} {self.arg2} {self.result}"


class IntermediateCodeGenerator:
    def __init__(self):
        self.code: List[ThreeAddressCode] = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self) -> str:
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def new_label(self) -> str:
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def emit(self, op: str, arg1: Optional[str] = None,
             arg2: Optional[str] = None, result: Optional[str] = None):
        instruction = ThreeAddressCode(op, arg1, arg2, result)
        self.code.append(instruction)

    def generate(self, ast: ASTNode) -> List[ThreeAddressCode]:
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0
        self.visit(ast)
        return self.code

    def visit(self, node: ASTNode) -> Optional[str]:
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        raise Exception(f"No existe metodo visit_{type(node).__name__}")

    def visit_ProgramNode(self, node: ProgramNode) -> None:
        for statement in node.statements:
            self.visit(statement)

    def visit_VarDeclarationNode(self, node: VarDeclarationNode) -> None:
        pass

    def visit_AssignmentNode(self, node: AssignmentNode) -> None:
        expr_result = self.visit(node.expression)
        self.emit('ASSIGN', expr_result, None, node.identifier)

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_result = self.visit(node.left)
        right_result = self.visit(node.right)
        temp = self.new_temp()
        self.emit(node.operator, left_result, right_result, temp)
        return temp

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> str:
        operand_result = self.visit(node.operand)
        temp = self.new_temp()

        if node.operator == '-':
            self.emit('UNARY_MINUS', operand_result, None, temp)
        elif node.operator == '+':
            self.emit('UNARY_PLUS', operand_result, None, temp)

        return temp

    def visit_NumberNode(self, node: NumberNode) -> str:
        return str(node.value)

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        return node.name

    def visit_IfNode(self, node: IfNode) -> None:
        condition_result = self.visit(node.condition)
        label_else = self.new_label()
        label_end = self.new_label()

        self.emit('IF_FALSE', condition_result, None, label_else)

        for stmt in node.then_block:
            self.visit(stmt)

        self.emit('GOTO', None, None, label_end)
        self.emit('LABEL', None, None, label_else)

        if node.else_block:
            for stmt in node.else_block:
                self.visit(stmt)

        self.emit('LABEL', None, None, label_end)

    def visit_WhileNode(self, node: WhileNode) -> None:
        label_start = self.new_label()
        label_end = self.new_label()

        self.emit('LABEL', None, None, label_start)
        condition_result = self.visit(node.condition)
        self.emit('IF_FALSE', condition_result, None, label_end)

        for stmt in node.body:
            self.visit(stmt)

        self.emit('GOTO', None, None, label_start)
        self.emit('LABEL', None, None, label_end)

    def visit_PrintNode(self, node: PrintNode) -> None:
        expr_result = self.visit(node.expression)
        self.emit('PRINT', expr_result, None, None)

    def print_code(self):
        print("\n" + "="*80)
        print("CODIGO INTERMEDIO (CODIGO DE TRES DIRECCIONES)")
        print("="*80)
        print(f"{'#':<5} {'Instruccion':<50}")
        print("-"*80)

        for i, instruction in enumerate(self.code):
            print(f"{i:<5} {str(instruction):<50}")

        print("="*80)
        print(f"Total de instrucciones: {len(self.code)}")
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

    if (suma > 25) {
        print(100);
    } else {
        print(0);
    }
    """

    print("Codigo fuente:")
    print(codigo)

    lexer = Lexer(codigo)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    generator = IntermediateCodeGenerator()
    intermediate_code = generator.generate(ast)

    generator.print_code()
