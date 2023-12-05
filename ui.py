from tkinter import filedialog
from lexer.lexer import Lexer
from tkinter.ttk import Treeview

from tkinter import *
# reference 
# https://www.youtube.com/watch?v=p7I92IMFa3c&ab_channel=Atlas
# https://www.tutorialspoint.com/python/tk_pack.htm -> for pack
# https://www.pythontutorial.net/tkinter/tkinter-treeview/ for tree
# https://coderslegacy.com/python/libraries-in-python/python-tkinter-filedialog/ -> for choosing file
def file_explorer_func(text_editor,pair):
    file = filedialog.askopenfilename(title="Select a File", filetypes=(("LOL files", "*.lol"),))


    if file:
        code = ""
        with open(file, "r") as fp:
            code = fp.read()
        lexer = Lexer(code, debug=False)
        # delete the current state of text editor when you insert a file
        text_editor.delete("1.0", "end")
        # insert the code to the text editor
        text_editor.insert("1.0", code) 
        arrayOflexemes = lexer.get_lexemes()
        print("========================================")
        for lexeme in arrayOflexemes:
            pair.insert("", "end", values=(lexeme.lexeme, lexeme.classification))

        print(arrayOflexemes[0].lexeme)
        print(arrayOflexemes[0].classification)


def layoutTheUi(root):


    root.title("Prelog") 
    root.geometry("800x800")
    root.minsize(800, 800)

    # top part of our  UI
    main_stage = Frame(root, bg="#fff") 
    main_stage.pack(side ="top",fill="both", expand=1)

    top_frame = Frame(main_stage, bg="gray22")
    top_frame.pack(side="top",fill="x",pady=10)

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
    symbol_label.pack(side="left", fill="x", pady=5,expand=1)
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

    bottom_frame = Frame(main_stage, bg="gray")
    bottom_frame.pack(side="top",fill="x",pady=10)

 # file explorer
    file_explorer = Button(top_left_frame, bg="blue", fg="white", text="File Explorer", command=lambda: file_explorer_func(text_editor, pair))
    file_explorer.pack(side="top", fill="x", pady=5)

    execute = Button(bottom_frame,bg="blue",fg="white",text="Execute")
    execute.pack(side="top",fill="x",pady=5,padx=10)

    console = Text(bottom_frame, state=NORMAL, height=20, width=30, font=("Courier New", 12))
    console.pack(side="top", fill="both", pady=(5, 5), padx=(5, 0))

