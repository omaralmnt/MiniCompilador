import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
from compilador import Compiler
from lexico import LexicalError
from sintactico import SyntaxError
from semantico import SemanticError


class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador MiniLang")
        self.root.geometry("1200x800")

        self.setup_styles()

        self.current_file = None
        self.compiler = Compiler()

        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()

        self.load_example(0)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        self.bg_color = "#1e1e1e"
        self.fg_color = "#d4d4d4"
        self.accent_color = "#007acc"
        self.error_color = "#f48771"
        self.success_color = "#4ec9b0"

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Guardar como...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)

        compile_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Compilar", menu=compile_menu)
        compile_menu.add_command(label="Compilar", command=self.compile_code, accelerator="F5")
        compile_menu.add_command(label="Limpiar resultados", command=self.clear_results)

        examples_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ejemplos", menu=examples_menu)
        examples_menu.add_command(label="Ejemplo 1: Suma simple", command=lambda: self.load_example(0))
        examples_menu.add_command(label="Ejemplo 2: If-Else", command=lambda: self.load_example(1))
        examples_menu.add_command(label="Ejemplo 3: Bucle While", command=lambda: self.load_example(2))
        examples_menu.add_command(label="Ejemplo 4: Factorial", command=lambda: self.load_example(3))

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Sintaxis MiniLang", command=self.show_syntax_help)
        help_menu.add_command(label="Acerca de", command=self.show_about)

        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.compile_code())

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg="#2d2d30", height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_new = tk.Button(toolbar, text="Nuevo", command=self.new_file,
                           bg="#2d2d30", fg="white", relief=tk.FLAT, padx=10)
        btn_new.pack(side=tk.LEFT, padx=5, pady=5)

        btn_open = tk.Button(toolbar, text="Abrir", command=self.open_file,
                            bg="#2d2d30", fg="white", relief=tk.FLAT, padx=10)
        btn_open.pack(side=tk.LEFT, padx=5, pady=5)

        btn_save = tk.Button(toolbar, text="Guardar", command=self.save_file,
                            bg="#2d2d30", fg="white", relief=tk.FLAT, padx=10)
        btn_save.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Frame(toolbar, bg="#404040", width=2).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        btn_compile = tk.Button(toolbar, text="Compilar (F5)", command=self.compile_code,
                               bg="#0e639c", fg="white", relief=tk.FLAT, padx=15, font=("Arial", 10, "bold"))
        btn_compile.pack(side=tk.LEFT, padx=5, pady=5)

        btn_clear = tk.Button(toolbar, text="Limpiar", command=self.clear_results,
                             bg="#2d2d30", fg="white", relief=tk.FLAT, padx=10)
        btn_clear.pack(side=tk.LEFT, padx=5, pady=5)

    def create_main_layout(self):
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, bg="#2d2d30")
        main_paned.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_paned, bg="#1e1e1e")
        main_paned.add(left_frame, width=600)

        editor_label = tk.Label(left_frame, text="Editor de Codigo MiniLang",
                               bg="#2d2d30", fg="white", font=("Arial", 11, "bold"), pady=5)
        editor_label.pack(fill=tk.X)

        editor_frame = tk.Frame(left_frame, bg="#1e1e1e")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.code_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            selectbackground="#264f78",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)

        self.setup_syntax_highlighting()
        self.code_editor.bind('<KeyRelease>', self.on_key_release)

        right_frame = tk.Frame(main_paned, bg="#1e1e1e")
        main_paned.add(right_frame, width=600)

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tokens_text = self.create_result_tab("Tokens")
        self.ast_text = self.create_result_tab("AST")
        self.symbols_text = self.create_result_tab("Simbolos")
        self.intermediate_text = self.create_result_tab("Codigo Intermedio")
        self.console_text = self.create_result_tab("Consola", bg="#0c0c0c")

    def create_result_tab(self, title, bg="#1e1e1e"):
        frame = tk.Frame(self.notebook, bg=bg)
        self.notebook.add(frame, text=title)

        text_widget = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=bg,
            fg="#d4d4d4",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        return text_widget

    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text="Listo",
            bg="#007acc",
            fg="white",
            anchor=tk.W,
            font=("Arial", 9),
            padx=10,
            pady=3
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_syntax_highlighting(self):
        self.code_editor.tag_configure("keyword", foreground="#569cd6")
        self.code_editor.tag_configure("number", foreground="#b5cea8")
        self.code_editor.tag_configure("string", foreground="#ce9178")
        self.code_editor.tag_configure("comment", foreground="#6a9955")
        self.code_editor.tag_configure("operator", foreground="#d4d4d4")

    def on_key_release(self, event=None):
        self.highlight_syntax()

    def highlight_syntax(self):
        for tag in ["keyword", "number", "comment", "operator"]:
            self.code_editor.tag_remove(tag, "1.0", tk.END)

        code = self.code_editor.get("1.0", tk.END)

        keywords = r'\b(var|if|else|while|print)\b'
        for match in re.finditer(keywords, code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("keyword", start, end)

        numbers = r'\b\d+\.?\d*\b'
        for match in re.finditer(numbers, code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("number", start, end)

        comments = r'//.*?$'
        for match in re.finditer(comments, code, re.MULTILINE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_editor.tag_add("comment", start, end)

    def new_file(self):
        if messagebox.askyesno("Nuevo archivo", "Deseas crear un nuevo archivo? Se perderan los cambios no guardados."):
            self.code_editor.delete("1.0", tk.END)
            self.current_file = None
            self.clear_results()
            self.update_status("Nuevo archivo creado")

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("MiniLang Files", "*.ml"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", content)
                self.current_file = filepath
                self.highlight_syntax()
                self.update_status(f"Archivo abierto: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")

    def save_file(self):
        if self.current_file:
            try:
                content = self.code_editor.get("1.0", tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status(f"Archivo guardado: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        filepath = filedialog.asksaveasfilename(
            title="Guardar archivo como",
            defaultextension=".ml",
            filetypes=[("MiniLang Files", "*.ml"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if filepath:
            try:
                content = self.code_editor.get("1.0", tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_file = filepath
                self.update_status(f"Archivo guardado: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def compile_code(self):
        self.clear_results()

        code = self.code_editor.get("1.0", tk.END).strip()

        if not code:
            messagebox.showwarning("Advertencia", "No hay codigo para compilar")
            return

        self.update_status("Compilando...", "#ff8800")
        self.root.update()

        import io
        from contextlib import redirect_stdout

        self.compiler = Compiler()

        try:
            f = io.StringIO()
            with redirect_stdout(f):
                from lexico import Lexer
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                lexer.print_tokens()
            self.tokens_text.insert("1.0", f.getvalue())

            f = io.StringIO()
            with redirect_stdout(f):
                from sintactico import Parser
                parser = Parser(tokens)
                ast = parser.parse()
                print("ARBOL DE SINTAXIS ABSTRACTA (AST)")
                print("="*80)
                parser.print_ast(ast)
            self.ast_text.insert("1.0", f.getvalue())

            f = io.StringIO()
            with redirect_stdout(f):
                from semantico import SemanticAnalyzer
                analyzer = SemanticAnalyzer()
                symbol_table = analyzer.analyze(ast)
                analyzer.print_results()
                symbol_table.print_table()
            self.symbols_text.insert("1.0", f.getvalue())

            f = io.StringIO()
            with redirect_stdout(f):
                from codigo_intermedio import IntermediateCodeGenerator
                generator = IntermediateCodeGenerator()
                intermediate_code = generator.generate(ast)
                generator.print_code()
            self.intermediate_text.insert("1.0", f.getvalue())

            self.console_text.insert("1.0", "COMPILACION EXITOSA\n\n")
            self.console_text.insert(tk.END, "Todas las fases completadas correctamente.\n")
            self.console_text.insert(tk.END, f"Total de tokens: {len(tokens)-1}\n")
            self.console_text.insert(tk.END, f"Total de simbolos: {len(symbol_table.get_all_symbols())}\n")
            self.console_text.insert(tk.END, f"Total de instrucciones: {len(intermediate_code)}\n")

            self.update_status("Compilacion exitosa", "#4ec9b0")
            messagebox.showinfo("Exito", "Compilacion completada exitosamente")

        except (LexicalError, SyntaxError, SemanticError) as e:
            self.console_text.insert("1.0", f"ERROR DE COMPILACION\n\n{str(e)}\n")
            self.update_status("Error de compilacion", "#f48771")
            messagebox.showerror("Error de Compilacion", str(e))

        except Exception as e:
            self.console_text.insert("1.0", f"ERROR INESPERADO\n\n{str(e)}\n")
            self.update_status("Error inesperado", "#f48771")
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")

    def clear_results(self):
        self.tokens_text.delete("1.0", tk.END)
        self.ast_text.delete("1.0", tk.END)
        self.symbols_text.delete("1.0", tk.END)
        self.intermediate_text.delete("1.0", tk.END)
        self.console_text.delete("1.0", tk.END)
        self.update_status("Resultados limpiados")

    def load_example(self, example_num):
        examples = [
            """var x;
var y;
var suma;

x = 10;
y = 20;
suma = x + y;

print(suma);""",

            """var a;
var b;
var resultado;

a = 15;
b = 10;

if (a > b) {
    resultado = 1;
    print(resultado);
} else {
    resultado = 0;
    print(resultado);
}""",

            """var contador;
var limite;

contador = 0;
limite = 5;

while (contador < limite) {
    print(contador);
    contador = contador + 1;
}""",

            """var numero;
var factorial;
var i;

numero = 5;
factorial = 1;
i = 1;

while (i <= numero) {
    factorial = factorial * i;
    i = i + 1;
}

print(factorial);"""
        ]

        if 0 <= example_num < len(examples):
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", examples[example_num])
            self.highlight_syntax()
            self.clear_results()
            self.update_status(f"Ejemplo {example_num + 1} cargado")

    def show_syntax_help(self):
        help_text = """SINTAXIS DE MINILANG

Declaracion de variables:
    var nombre;

Asignacion:
    nombre = expresion;

Operadores aritmeticos:
    +  -  *  /

Operadores de comparacion:
    ==  !=  <  >  <=  >=

Condicionales:
    if (condicion) {
    } else {
    }

Bucles:
    while (condicion) {
    }

Imprimir:
    print(expresion);

Comentarios:
    // comentario de una linea
        """

        messagebox.showinfo("Sintaxis MiniLang", help_text)

    def show_about(self):
        about_text = """COMPILADOR MINILANG
Version 1.0

Un compilador completo implementado en Python

- Analisis Lexico
- Analisis Sintactico
- Analisis Semantico
- Tabla de Simbolos
- Generacion de Codigo Intermedio
        """

        messagebox.showinfo("Acerca de", about_text)

    def update_status(self, message, color="#007acc"):
        self.status_bar.config(text=message, bg=color)


def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
