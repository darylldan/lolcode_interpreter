from parser.statement import Statement
from lexer.token_class import TokenClass
from parser.expression import Expression
from semantics.symbol_table import SymbolTable

'''
Each function has a separated symbol table, with its separate
IT variable. The symbol table contains all the parameters passed onto the function.
'''
class FunctionStatement(Statement):
    def __init__(self,
                how_iz_i: TokenClass,
                funcident: TokenClass = None,
                if_u_say_so: TokenClass = None
        ) -> None:
        super().__init__()
        self.how_iz_i = how_iz_i
        self.funcident: TokenClass = funcident
        self.params: list[TokenClass] = []
        self.statements: list[Statement] = []
        self.if_u_say_so = if_u_say_so
        self.sym_table = SymbolTable()
        
    def in_params(self, var: TokenClass) -> bool:
        for p in self.params:
            if p.lexeme == var.lexeme:
                return True
            
        return False

    def add_param(self, var: TokenClass) -> bool:
        if self.in_params(var):
            return False
        
        self.params.append(var)

    def add_statement(self, statement: Statement):
        self.statements.append(statement)

class FunctionCallStatement(Statement):
    def __init__(self, i_iz: TokenClass, func_ident: TokenClass):
        self.i_iz = i_iz
        self.func_ident = func_ident
        self.args: list[TokenClass | Expression] = []

    def add_arg(self, param: (TokenClass | Expression)) -> None:
        self.args.append(param)

    def get_args(self) -> list[TokenClass | Expression]:
        return self.args
    
    def get_args_count(self) -> int:
        return len(self.args)
    
    def get_fnident_str(self) -> str:
        return self.func_ident.lexeme

class FunctionReturn(Statement):
    def __init__(self, ret_keyword: TokenClass, return_val: (TokenClass | Expression) = None):
        self.ret_keyword = ret_keyword
        self.return_val = return_val
       