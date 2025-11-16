import sys
from lexico import Lexer, LexicalError
from sintactico import Parser, SyntaxError
from semantico import SemanticAnalyzer, SemanticError
from codigo_intermedio import IntermediateCodeGenerator


class Compiler:
    def __init__(self):
        self.source_code = ""
        self.tokens = []
        self.ast = None
        self.symbol_table = None
        self.intermediate_code = []

    def compile(self, source_code: str, verbose: bool = True):
        self.source_code = source_code

        try:
            if verbose:
                print("\n" + "="*80)
                print("COMPILADOR MINILANG")
                print("="*80)
                print("\nFASE 1: ANALISIS LEXICO")
                print("-"*80)

            lexer = Lexer(source_code)
            self.tokens = lexer.tokenize()

            if verbose:
                print(f"Analisis lexico completado: {len(self.tokens)-1} tokens encontrados")
                lexer.print_tokens()

            if verbose:
                print("\nFASE 2: ANALISIS SINTACTICO")
                print("-"*80)

            parser = Parser(self.tokens)
            self.ast = parser.parse()

            if verbose:
                print("Analisis sintactico completado")
                print("\n" + "="*80)
                print("ARBOL DE SINTAXIS ABSTRACTA (AST)")
                print("="*80 + "\n")
                parser.print_ast(self.ast)

            if verbose:
                print("\nFASE 3: ANALISIS SEMANTICO")
                print("-"*80)

            analyzer = SemanticAnalyzer()
            self.symbol_table = analyzer.analyze(self.ast)

            if verbose:
                print("Analisis semantico completado")
                analyzer.print_results()
                self.symbol_table.print_table()

            if verbose:
                print("\nFASE 4: GENERACION DE CODIGO INTERMEDIO")
                print("-"*80)

            generator = IntermediateCodeGenerator()
            self.intermediate_code = generator.generate(self.ast)

            if verbose:
                print("Generacion de codigo intermedio completada")
                generator.print_code()

            if verbose:
                print("\n" + "="*80)
                print("COMPILACION EXITOSA")
                print("="*80 + "\n")

            return True

        except LexicalError as e:
            print("\n" + "="*80)
            print("ERROR LEXICO")
            print("="*80)
            print(f"\n{str(e)}\n")
            print("="*80 + "\n")
            return False

        except SyntaxError as e:
            print("\n" + "="*80)
            print("ERROR SINTACTICO")
            print("="*80)
            print(f"\n{str(e)}\n")
            print("="*80 + "\n")
            return False

        except SemanticError as e:
            print("\n" + "="*80)
            print("ERROR SEMANTICO")
            print("="*80)
            print(f"\n{str(e)}\n")
            print("="*80 + "\n")
            return False

        except Exception as e:
            print("\n" + "="*80)
            print("ERROR INESPERADO")
            print("="*80)
            print(f"\n{str(e)}\n")
            print("="*80 + "\n")
            return False

    def compile_file(self, filepath: str, verbose: bool = True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source_code = f.read()

            print(f"\nCompilando archivo: {filepath}")
            print("-"*80)
            print("Codigo fuente:")
            print("-"*80)
            print(source_code)
            print("-"*80)

            return self.compile(source_code, verbose)

        except FileNotFoundError:
            print(f"\nError: No se encontro el archivo '{filepath}'")
            return False
        except Exception as e:
            print(f"\nError al leer el archivo: {str(e)}")
            return False


def main():
    compiler = Compiler()

    print("\n" + "="*80)
    print("EJEMPLO 1: Programa simple")
    print("="*80)

    codigo_ejemplo1 = """
    var x;
    var y;
    x = 10;
    y = 20;
    var suma;
    suma = x + y;
    print(suma);
    """

    compiler.compile(codigo_ejemplo1, verbose=True)

    print("\n\n" + "="*80)
    print("EJEMPLO 2: Programa con if-else")
    print("="*80)

    codigo_ejemplo2 = """
    var a;
    var b;
    a = 15;
    b = 10;

    if (a > b) {
        print(1);
    } else {
        print(0);
    }
    """

    compiler.compile(codigo_ejemplo2, verbose=True)

    print("\n\n" + "="*80)
    print("EJEMPLO 3: Programa con bucle while")
    print("="*80)

    codigo_ejemplo3 = """
    var contador;
    var limite;
    contador = 0;
    limite = 5;

    while (contador < limite) {
        print(contador);
        contador = contador + 1;
    }
    """

    compiler.compile(codigo_ejemplo3, verbose=True)

    print("\n\n" + "="*80)
    print("EJEMPLO 4: Programa con error (variable no declarada)")
    print("="*80)

    codigo_ejemplo4 = """
    var x;
    x = 10;
    y = 20;
    print(x);
    """

    compiler.compile(codigo_ejemplo4, verbose=True)


if __name__ == "__main__":
    main()
