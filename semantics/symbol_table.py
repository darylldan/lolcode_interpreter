from lexer.token_type import TokenType
from semantics.symbol import Symbol

class SymbolTable():
    def __init__(self):
        self.sym_table: dict = {
            "IT": SymbolTable("NOOB", TokenType.NOOB)
        }

    def indentifier_exists(self, identifier: str) -> bool:
        return identifier in self.sym_table.keys()

    def add_symbol(self, identifier: str, value: Symbol) -> bool:
        if self.indentifier_exists(identifier):
            return False
        
        self.sym_table[identifier] = value

    def modify_symbol(self, identifier, value: Symbol) -> bool:
        if not self.indentifier_exists(identifier):
            return False
        
        self.sym_table[identifier] = value

    def retrieve_val(self, identifier: str) -> Symbol:
        if not self.indentifier_exists(identifier):
            return None
        
        return self.sym_table[identifier]
    
    def get_IT(self) -> Symbol:
        return self.sym_table["IT"]
    
    def set_IT(self, value: any) -> (any | None):
        self.sym_table["IT"] = value

    def get_sym_table(self) -> dict:
        return self.sym_table