
from tkinter.ttk import Treeview
from lexer.lexer import Lexer
import re

from tkinter import *
from tkinter.ttk import *
from ui import layoutTheUi

def get_code_line(line: int, src):
    code = ""
    temp_line = 1
    for c in src:
        if temp_line == line + 1:
            break

        if c == '\n':
            temp_line += 1
            
        if temp_line == line:
            code += c

    
    return code



# print(get_code_line(4, code))

# for c in code:
#     if c == "\n":
#         print("newline")


# print([str(x) for x in lexer.get_lexemes()])


root = Tk()
layoutTheUi(root)

root.mainloop()