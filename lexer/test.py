from lexer import Lexer
import re
from token_type import TokenType
from tkinter import *
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

file = "short_tc.lol"

code = ""
with open(file, "r") as fp:
    code = fp.read()

# print(get_code_line(4, code))

# for c in code:
#     if c == "\n":
#         print("newline")

lexer = Lexer(code, debug=False)
print([str(x) for x in lexer.get_lexemes()])

root = Tk()
root.title("Prelog")

gameStatus = Label(root, text="haha", font=("Terminal", 18), relief="solid", borderwidth=2,padx=50, pady=20)
gameStatus.grid(row=0, column=0, columnspan=6,pady=10)

# Start the Tkinter event loop
root.mainloop()