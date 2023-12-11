from lexer.lexer import Lexer
from parser.parser import Parser
from parser.expression import StringConcatenation
from lexer.token_class import TokenClass
from lexer.token_type import TokenType

# code = ""

# with open("simple.lol", "r") as fp:
#     code = fp.read()

# x = Lexer(code)
# y = x.get_lexemes()

# a = Parser(y, code)

x = StringConcatenation(TokenClass(TokenType.SMOOSH, "", "", "", 1), [])

print(isinstance(x, StringConcatenation))