from lexer import Lexer
import re
from token_type import TokenType

file = "test_case_noerr.lol"

code = []
with open(file, "r") as fp:
    code = fp.readlines()

for i in range(0, len(code)):
    code[i] = code[i].strip()

src = ''.join(code)
# print(src)

lexer = Lexer(src)
print(lexer.get_lexemes())

# x = "B"
# print(re.match(TokenType.BTW.value))