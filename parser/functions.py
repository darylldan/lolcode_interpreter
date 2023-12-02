from statement import Statement
from lexer.token_class import TokenClass
from expression import Expression

class FunctionStatement(Statement):
    def __init__(self,
                how_iz_i: TokenClass,
                funcident: TokenClass,
                params: list[TokenClass],
                statements: list[Statement],
                if_u_say_so: TokenClass
        ) -> None:
        super().__init__()
        self.how_iz_i = how_iz_i
        self.funcident: funcident
        self.params = params
        self.statements = statements
        self.if_u_say_so = if_u_say_so
        
class FunctionCallStatement(Statement):
    def __init__(self, i_iz: TokenClass, args: list[TokenClass | Expression]):
        self.i_iz = i_iz
        self.args = args

class FunctionReturn(Statement):
    def __init__(self, ret_keyword: TokenClass, return_val: (TokenClass | Expression) = None):
        self.ret_keyword = ret_keyword
        self.return_val = return_val