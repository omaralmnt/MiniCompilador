from dataclasses import dataclass
from typing import Dict, Optional, Any
from enum import Enum, auto


class SymbolType(Enum):
    VARIABLE = auto()
    CONSTANT = auto()


@dataclass
class Symbol:
    name: str
    symbol_type: SymbolType
    data_type: Optional[str] = None
    value: Optional[Any] = None
    line: int = 0
    initialized: bool = False
    used: bool = False

    def __repr__(self):
        return (f"Symbol(name='{self.name}', type={self.symbol_type.name}, "
                f"data_type={self.data_type}, initialized={self.initialized}, "
                f"used={self.used}, line={self.line})")


class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.scopes: list = [{}]

    def declare(self, name: str, symbol_type: SymbolType, line: int,
                data_type: Optional[str] = None, value: Optional[Any] = None) -> Symbol:
        if name in self.symbols:
            existing_symbol = self.symbols[name]
            raise Exception(
                f"Error semantico: Variable '{name}' ya declarada en linea {existing_symbol.line}. "
                f"Redeclaracion en linea {line}."
            )

        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            data_type=data_type,
            value=value,
            line=line,
            initialized=(value is not None)
        )

        self.symbols[name] = symbol
        return symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    def exists(self, name: str) -> bool:
        return name in self.symbols

    def update_value(self, name: str, value: Any):
        if name not in self.symbols:
            raise Exception(f"Error semantico: Variable '{name}' no declarada.")

        symbol = self.symbols[name]
        symbol.value = value
        symbol.initialized = True

        if symbol.data_type is None:
            if isinstance(value, int):
                symbol.data_type = 'int'
            elif isinstance(value, float):
                symbol.data_type = 'float'

    def mark_as_used(self, name: str):
        if name not in self.symbols:
            raise Exception(f"Error semantico: Variable '{name}' no declarada.")

        self.symbols[name].used = True

    def mark_as_initialized(self, name: str):
        if name not in self.symbols:
            raise Exception(f"Error semantico: Variable '{name}' no declarada.")

        self.symbols[name].initialized = True

    def get_all_symbols(self) -> Dict[str, Symbol]:
        return self.symbols.copy()

    def get_warnings(self) -> list:
        warnings = []

        for name, symbol in self.symbols.items():
            if not symbol.used:
                warnings.append(
                    f"Advertencia: Variable '{name}' declarada en linea {symbol.line} "
                    f"pero nunca usada."
                )

            if symbol.used and not symbol.initialized:
                warnings.append(
                    f"Advertencia: Variable '{name}' usada en el programa "
                    f"pero podria no estar inicializada (declarada en linea {symbol.line})."
                )

        return warnings

    def print_table(self):
        print("\n" + "="*80)
        print("TABLA DE SIMBOLOS")
        print("="*80)
        print(f"{'Nombre':<15} {'Tipo':<12} {'Tipo Dato':<12} {'Valor':<12} "
              f"{'Linea':<8} {'Init':<6} {'Usado':<6}")
        print("-"*80)

        for name, symbol in sorted(self.symbols.items()):
            value_str = str(symbol.value) if symbol.value is not None else "None"
            data_type_str = symbol.data_type if symbol.data_type else "?"

            print(f"{symbol.name:<15} {symbol.symbol_type.name:<12} {data_type_str:<12} "
                  f"{value_str:<12} {symbol.line:<8} {str(symbol.initialized):<6} "
                  f"{str(symbol.used):<6}")

        print("="*80)
        print(f"Total de simbolos: {len(self.symbols)}")
        print("="*80 + "\n")

        warnings = self.get_warnings()
        if warnings:
            print("ADVERTENCIAS:")
            print("-"*80)
            for warning in warnings:
                print(f"  {warning}")
            print("="*80 + "\n")

    def clear(self):
        self.symbols.clear()
        self.scopes = [{}]


if __name__ == "__main__":
    tabla = SymbolTable()

    tabla.declare("x", SymbolType.VARIABLE, line=1)
    tabla.declare("y", SymbolType.VARIABLE, line=2)
    tabla.declare("suma", SymbolType.VARIABLE, line=5)

    tabla.update_value("x", 10)
    tabla.update_value("y", 20)

    tabla.mark_as_used("x")
    tabla.mark_as_used("y")
    tabla.mark_as_used("suma")

    tabla.update_value("suma", 30)

    tabla.print_table()
