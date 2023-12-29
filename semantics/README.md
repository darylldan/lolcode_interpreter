### Adding implementation for a statement:

- Add implementation to `execute_statement()` function.
- Implementation starts with checking the instance of the statement, use `isinstance(statement, <Statement Class>)` on an `if`-clause, and code the implementation in the body.
- Upon successful execution of the statement, always return `True`. If statement execution resulted in an error, return `False` instead.
- Check the class structure of the statement in the `/parser` folder to check the name of class attribute that holds the parameter/argument of the statement or other necessary tokens that is used in execution of the statement.
- Use `evaluate_expression(exr: Expression)` to evaluate expressions. It assumes that the arguments passed onto it is an instance of an `Expression` class so make sure that you are checking it first. You can use `isinstance(expr, Expression)` to check if an object is an expression.
- To modify a value to a symbol table, use `self.sym_table.modify_symbol(varident.lexeme, Symbol(<actual value>, <(Type.Yarn | Type.NUBMR | Type.NUMBAR | Type.TROOF | Type.NOOB)>))`. You can use `self.get_type()` if the type of the value can only be known on runtime, or if you are unsure of the type. It will be `self.sym_table.modify_symbol(varident.lexeme, Symbol(<actual value>, self.get_type(<actual value>)))`.
- Methods of the symbol table can be found in the class declaration inside `symbol_table.py`.
- When retrieving value of a variable from the symbol table, it could return `None` if the variable is nonexistent. If it returned `None`, print an `Error.REFERENCED_UNDEFINED_VAR` using `self.printError(Errors.REFERENCED_UNDEFINED_VAR, statement.varident)`. Change the `TokenClass` argument accordingly.
- `self.retrieve_val(identifier: str)` accepts a variable name string. Name string could be attained from a `TokenClass` with a `token_type` of `TokenType.VARIDENT` using `<token class name>.lexeme`. It returns a `Symbol` object and to access its value, use its `value` attribute (`symbol.value`).
- Most statement involves modifying the symbol table.
- Input/Output is temporarily done in the python terminal, not in the `UI`. Modify `simple.lol` and run `test.py` to test the code.
- Most of the bugs ay nasa expression parser HAHAHAHAHABNA HIRAP XORI XORI