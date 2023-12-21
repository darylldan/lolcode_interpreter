from lexer.token_type import TokenType
from semantics.symbol import Symbol

class SymbolTable():
    def __init__(self):
        self.sym_table: dict[str, Symbol] = {
            "IT": Symbol("NOOB", TokenType.NOOB)
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
        return True

    def retrieve_val(self, identifier: str) -> Symbol:
        if not self.indentifier_exists(identifier):
            return None
        
        return self.sym_table[identifier]
    
    def get_IT(self) -> Symbol:
        return self.sym_table["IT"]
    
    def set_IT(self, value: Symbol):
        self.sym_table["IT"] = value

    def get_sym_table(self) -> dict:
        return self.sym_table
    
    def __print_sym__(self):
        print("c\tident\tval\ttype")

        c = 0
        for i in self.sym_table.keys():
            print(f"{c}\t{i}\t{self.sym_table[i].value}\t{self.sym_table[i].type}")
            c += 1