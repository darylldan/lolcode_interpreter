from tkinter import filedialog
from lexer.lexer import Lexer
from misc.terminal import Terminal
from parser.parser import Parser
from tkinter.ttk import Treeview
from semantics.sem_analyzer import SemanticAnalyzer
import copy

from tkinter import *
# reference 
# https://www.youtube.com/watch?v=p7I92IMFa3c&ab_channel=Atlas
# https://www.tutorialspoint.com/python/tk_pack.htm -> for pack
# https://www.pythontutorial.net/tkinter/tkinter-treeview/ for tree
# https://coderslegacy.com/python/libraries-in-python/python-tkinter-filedialog/ -> for choosing file

global_root = None
global_console = None

def file_explorer_func(text_editor):
    file = filedialog.askopenfilename(title="Select a File", filetypes=(("LOL files", "*.lol"),))
    if file:
        code = ""
        with open(file, "r") as fp:
            code = fp.read()
        text_editor.delete("1.0", "end")
        text_editor.insert("1.0", code) 
      
def console_func(console):
    console.insert("1.0", "Hello World")

def execute_func(text_editor,pair,pair2,console):
    code = text_editor.get("1.0", "end-1c") 
    if not code:
        return
    else:
        console.clear()
  
        lexer = Lexer(code, debug=False)
        arrayOflexemes = lexer.get_lexemes()
        parser = Parser(copy.deepcopy(arrayOflexemes), code)
        if parser.successful_parsing:
            semantic = SemanticAnalyzer(parser.main_program,code, global_root, global_console)
            symbolsTable = semantic.get_sym_table()

            # dictionarySymbols = parser.get_symbols()

            print("========================================")
            print(arrayOflexemes)
            pair.delete(*pair.get_children())
            pair2.delete(*pair2.get_children())
            for lexeme in arrayOflexemes:
                pair.insert("", "end", values=(lexeme.lexeme, lexeme.classification))
            
            for symbol in symbolsTable.keys():
                pair2.insert("", "end", values=(symbol, symbolsTable[symbol].value))

def layoutTheUi(root):
    root.title("Prelog") 
    root.geometry("800x800")
    root.minsize(800, 800)

    global global_root
    global_root = root

    # top part of our  UI
    main_stage = Frame(root, bg="#fff") 
    main_stage.pack(side ="top",fill="both", )

    top_frame = Frame(main_stage, bg="gray22")  
    top_frame.pack(side="top",fill="x")

    ## parts of top frame 

    # Left side of the top (textEditor,fileExplorer)
    top_left_frame = Frame(top_frame, bg="green")
    top_left_frame.pack(side="left",fill="x",padx=5)
    text_editor_frame = Frame(top_left_frame, bg="pink")
    text_editor_frame.pack(side="bottom",fill="both",expand=1)
    # text editor
    text_editor = Text(text_editor_frame, state="normal", height=27, width=80, font=("Courier New", 8), wrap="none")
    text_editor.pack(side="top", fill="both", pady=(5, 5), padx=(5, 0))
    # x-axis scrollbar
    scroll_x = Scrollbar(text_editor_frame, command=text_editor.xview, orient=HORIZONTAL)
    scroll_x.pack(side="bottom", fill="x")
    text_editor.config(xscrollcommand=scroll_x.set)
   
    # Right side of the top (title, lexemes, symbol)
    top_right_frame = Frame(top_frame, bg="yellow")
    top_right_frame.pack(side="left",fill="x",padx=10)

    # title
    title = Label(top_right_frame, text="Prelog LOL CODE Interpreter", font=("Courier New", 10), bg="yellow")
    title.pack(side="top", fill="x", pady=5,expand=1)

    # labels for lexemes and symbols
    labels = Frame(top_right_frame, bg="orange")
    labels.pack(side="top", fill="x", pady=5,expand=1)

    # lexeme title
    lexeme_label = Label(labels, text="Lexemes", font=("Courier New", 10), bg="green")
    lexeme_label.pack(side="left", fill="x", pady=5,expand=1)

    # symbol title
    symbol_label = Label(labels, text="Symbols", font=("Courier New", 10), bg="green")
    symbol_label.pack(side="right", fill="x", pady=5,expand=1)
    # holder of lexemes and symbols
    rightBlock = Frame(top_right_frame, bg="white")
    rightBlock.pack(side="left", fill="both", expand=1)
    #Lexeme
    pair = Treeview(rightBlock, columns=("Lexeme", "Classification"), show="headings", height=17)
    pair.heading("Lexeme", text="Lexeme")
    pair.heading("Classification", text="Classification")

    pair.column("Lexeme", width=180)
    pair.column("Classification", width=220)
    pair.pack(side="left", fill="both", expand=1,padx=(10))

    # Symbols
    pair2 = Treeview(rightBlock, columns=("Identifier", "Value"), show="headings", height=17)
    pair2.heading("Identifier", text="Identifier")
    pair2.heading("Value", text="Value")

    pair2.column("Identifier", width=180)
    pair2.column("Value", width=150)
    pair2.pack(side="left", fill="both", expand=1,padx=(5))

    bottom_frame = Frame(main_stage, bg="red")     # bottom part
    bottom_frame.pack(side="bottom",fill="both",expand=1)

    # file explorer
    file_explorer = Button(top_left_frame, bg="blue", fg="white", text="File Explorer", command=lambda: file_explorer_func(text_editor))
    file_explorer.pack(side="top", fill="x", pady=5)
    
    # Console
    # console = Text(bottom_frame, state="disabled", height=10, width=30, font=("Courier New", 12))
    # console.pack(side="bottom", fill="both", pady=(5, 5), padx=(5, 5))
    # execute = Button(bottom_frame,bg="blue",fg="white",text="Execute", command=lambda: execute_func(text_editor, pair,pair2,console))
    # execute.pack(side="top",fill="both",padx=5, pady=(5, 0))


    console = Terminal(bottom_frame, StringVar())
    execute = Button(bottom_frame,bg="blue",fg="white",text="Execute", command=lambda: execute_func(text_editor, pair,pair2,console))
    execute.pack(side="top",fill="both",padx=5, pady=(5, 0))
    global global_console
    global_console = console