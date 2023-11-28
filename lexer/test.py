from lexer import Lexer
import re
from token_type import TokenType

file = "short_tc.lol"

code = ""
with open(file, "r") as fp:
    code = fp.read()

# print(code)

# for c in code:
#     if c == "\n":
#         print("newline")

lexer = Lexer(code)
print(lexer.get_lexemes())