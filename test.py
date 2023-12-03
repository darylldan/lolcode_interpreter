from lexer.lexer import Lexer
from parser.parser import Parser

code = ""

with open("simple.lol", "r") as fp:
    code = fp.read()

x = Lexer(code)
y = x.get_lexemes()

a = Parser(y, code)
