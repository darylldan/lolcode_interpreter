from lexer import Lexer
import re
from token_type import TokenType

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

file = "test_case_noerr.lol"

code = ""
with open(file, "r") as fp:
    code = fp.read()

# print(get_code_line(4, code))

# for c in code:
#     if c == "\n":
#         print("newline")

lexer = Lexer(code, silent=False)
print(lexer.get_lexemes())