from lexer.token_class import TokenClass
from parser.functions import FunctionStatement
import copy

class FunctionTable():
    def __init__(self):
        self.func_table: dict[str, FunctionStatement] = {}

    def is_func_defined(self, func_ident: str) -> bool:
        return func_ident in self.func_table.keys()
    
    def add_func(self, func_ident: str, func_statement: FunctionStatement) -> bool:
        if self.is_func_defined(func_ident):
            return False
        
        self.func_table[func_ident] = func_statement
        return True

    def retrieve_func(self, func_ident: str) -> (FunctionStatement | None):
        if not self.is_func_defined(func_ident):
            return None
        
        return copy.deepcopy(self.func_table[func_ident])