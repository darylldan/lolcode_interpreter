# Semantic Analyzer

## Gist
- Semantic analyzer uses the `Program` object produced by the parser to execute the lolcode program. It has a main symbol table which holds all the information about a variable which is their actual value and their type. Symbol table also has a default  global variable `IT`. The semantic analyzer is also responsible for executing the statements inside the program.
- It first evaluates all the variable declaration before it proceeds to statement execution. If all variable declaration, together with its assigned value, is valid, it now proceeds to statement parsing. All uninitialized variables has a value of `Noob.NOOB` which is a `null` in common programming language.
- It iterates through all the `statements: list[Statement]` attribute of the program, executing them one by one. The function `execute_statement(statement: Statement)` contains all the code for executing a specific statement. There are several statements that calls `execute_statement()` also such as the if-then statement or for-loop statement.
- Most of the statements modify the `sym_table` attribute of the program.
- If an error has been encountered, it prints the error and stops the execution of statements.

## Symbol Table
- The symbol table roughly follows the structure below:

    | Key: `str`   | Value:  `Symbol` |
    | ------------- | ------------- |
    | `IT`  | `Symbol(val = Noob.NOOB, type = TokenType.NOOB)` |
    | `var1`  | `Symbol(val = 42, type = TokenType.NUMBR_TYPE)` |
    | `var2`  | `Symbol(val = 123.123, type = TokenType.NUMBAR_TYPE)` |
    | `var3`  | `Symbol(val = 'hello' type = TokenType.YARN_TYPE)` |
    | `var4`  | `Symbol(val = False, type = TokenType.FAIL)` |

    - The symbol table is a dictionary that contains a `Symbol` object which contains the actual value of the variable and their type with their key being the string representation of the variable.

    - **Key**
        - The key is a string representation of the variable identifier. It can usually be accesed from a `TokenClass` with a `TokenType` of `TokenType.VARIDENT` using `token.lexeme`.
        - If a key is non existent, the symbol table returns a `None`. Such case must be handled everytime the `retrieve_val()` method of symbol table is used.

    - **Symbol**
        - The object that every key points to in the symbol table dictionary is a `Symbol` object.
        - The `Symbol` object has two class attributes:
            - `value: Any` - The actual value of the symbol/variable.
            - `type: TokenType` - The data type of the value.
        - Retrieving the actual value of a variable from the symbol table can take in the form of `sym_table.retrieve_val(varident.lexeme).value` (a case where it returns `None` must be handled and the appropriate error must be printed).

## Expression Evaluation
- Since all of the operations are in prefix format, nesting expressions (all expressions except `ANY OF`, `ALL OF`, and `SMOOSH`) are evaluated using a stack.

### Prefix Expression Evaluation Algorithm using Stack
> [!IMPORTANT]
> Expression evaluator assumes that the expression is valid. This must be caught on the parsing stage.

- Let's say you have an expression:
    ```
    SUM OF PRODUKT OF 3 AN 5 AN PRODUKT OF 7 AN 9
    ```
- The parser will store it in an array, with the separators removed:
    ```
    expr = [SUM OF, PRODUKT OF, 3, 5, PRODUKT OF, 7, 9]
    ```
- Have a stack with `push()` and `pop()` operations:
    ```
    stack = [ ]  # push() adds at index 0, pop() removes at index 0
    ```
- The algorithm that was used to evaluate the expression above is as follows:
    1. Reverse the expression array. The resulting expression array will be:
        ```
        expr = [9, 7, PRODUKT OF, 5, 3, PRODUKT OF, SUM OF]
        ```

    2. Pop from the `expr` array.
        - If the popped value is an operand, push it into the stack.
        - If the popped value is an operator, pop the required number of operands, perform the operation, and push back the result into the stack.

    3. Repeat the previous step until `expr` is empty.

    4. If `expr` is empty, return value of the top of stack. If an expression is valid, once `expr` is empty, `len(stack) == 1`.
- Continuing the example based from the algorithm above:
    ```
    expr = [9, 7, PRODUKT OF, 5, 3, PRODUKT OF, SUM OF]
    stack = [ ]
    ```

    1. Pop from `expr`. Popped value is an operand (`9`). Push to the stack.
        ```
        expr = [7, PRODUKT OF, 5, 3, PRODUKT OF, SUM OF]
        stack = [9]
        ```
    2. Pop from `expr`. Popped value is an operand (`7`). Push to the stack.
        ```
        expr = [PRODUKT OF, 5, 3, PRODUKT OF, SUM OF]
        stack = [7, 9]
        ```
    3. Pop from `expr`. Popped value is an operator (`PRODUKT OF`). Perform the operation. `PRODUKT OF` requires two operands, so pop two values from the stack, multiply them together and push the result back to the stack.
        ```
        expr = [5, 3, PRODUKT OF, SUM OF]
        stack = [63]
        ```
    4. Pop from `expr`. Popped value is an operand (`5`). Push to the stack.
        ```
        expr = [3, PRODUKT OF, SUM OF]
        stack = [5, 63]
        ```
    5. Pop from `expr`. Popped value is an operand (`3`). Push to the stack.
        ```
        expr = [PRODUKT OF, SUM OF]
        stack = [3, 5, 63]
        ```
    6. Pop from `expr`. Popped value is an operator (`PRODUKT OF`). Perform the operation. `PRODUKT OF` requires two operands, so pop two values from the stack, multiply them together and push the result back to the stack.
        ```
        expr = [SUM OF]
        stack = [15, 63]
        ```
    6. Pop from `expr`. Popped value is an operator (`PRODUKT OF`). Perform the operation. `SUM OF` requires two operands, so pop two values from the stack, add them together and push the result back to the stack.
        ```
        expr = []
        stack = [78]
        ```
    7. `expr` array is empty, the expression is successfully evaluated. Return the value of the top of stack.
        ```
        SUM OF PRODUKT OF 3 AN 5 AN PRODUKT OF 7 AN 9 = 78
        ```
- Same algorithm also works for boolean expressions and comparison expressions. It also technically works for nested expressions with different types.

### Retrieving Values of Operands
- Operands of an expression can be either a variable or a literal.
- The implementation of prefix expression evaluator on this semantics do not retrieve the values of variables immediately. Just like literals, variables are also pushed into the stack since they are a valid operand.
- When an operation token is popped from the stack, and one or both of the operands are variables, their values are then retrieved from the symbol table.
- Arithmetic operations and boolean operations automatically typecast their operands into numbers and booleans respectively.
- To solve the problem of retrieving variables and typecasting literals, the concept of `unwrapping` was implemented.
- The gist of every `unwrap` function is to obtain a literal by exhausting all the possible casting operations. `unwrap` functions checks first if the arguments passed onto it is a variable, if so, it retrieves it from the symbol table. Then depending on the type of `unwrap` function, it casts it into a specific data type, following the typecasting rules in the language specification.
    - `unwrap_num()` accepts either a `TokenClass` with a `TokenType` of `TokenType.VARIDENT` and tries to typecast the retrieved value into a number. It will always produce a number, or a `None` if the variable value or literal is not typecastable to number (either a `Noob.NOOB`, or a string that is not a valid number.)
    - `unwrap_bool()` accepts either a `TokenClass` with a `TokenType` of `TokenType.VARIDENT` and tries to typecast the retrieved value into a boolean. It will always produce a boolean, or a `None` if the variable value or literal is not typecastable to boolean.
    - `unwrap_str()` accepts either a `TokenClass` with a `TokenType` of `TokenType.VARIDENT` and tries to typecast the retrieved value into its string representation. It will always produce a string, or a `None` if the variable value or literal is not typecastable to string.
    - `unwrap_no_cast()` just retrieves the value from symbol table if the argument is passed into it. If a `TokenClass` literal is passed into it, it returns its literal value.
- The concept of unwrapping makes the implementation of the nesting expression evaluator easier as the means of retrieving a value is already abstracted.

### Evaluation of Infinite Arity Expression
- There are three expressions that accepts infinite arities:
    - `ALL OF` - Returns `True` if all its arguments evaluate into `True`.
    - `ANY OF` - Returns `True` if at least one of its arguments evaluate into `True`.
    - `SMOOSH` - String concatination function. Typecasts all of its arguments into string, concatinates them, and returns the resulting string.
- The arguments of `ALL OF` and `ANY OF` can either be a literal, variable, or a boolean expression. Evaluating the expression involves looping through all of its passed arguments and evaluating them. If the argument is a `TokenClass`, meaning it is either a variable or a literal, `unwrap_bool()` is used to evaluate them into a boolean. If the argument is a boolean expression, the expression is evaluated using the nesting expression evaluatior.
- `ANY OF` stops iterating though its argument once it encounters a `True` value.
- The arguments of `SMOOSH` can either be a string, literal, or a variable. Evaluating the expression involves looping through all of its passed arguments and getting its string representation. Their concatinated string is returned.

## Typecasting
- There are two implemented methods for typecasting a value into another type.
    - `cast_token_value` - Accepts a `TokenClass` object. Its `TokenType` must be a one of the literal types. The second parameter is the type that the value of the passed `TokenClass` object will be casted into.
    - `cast_literal_value` - Accepts a python literal. The second parameter is the type that the value of the passed literal will be casted into.

## Input/Output
- A `Terminal` class is passed into the `SemanticAnalyzer` class during its instantiation which is a Tkinter widget wrapped in a class.
- `Terminal` has methods of printing an output and getting an input from the user in which the `SemanticAnalyzer` utilizes everytime an input or an output statement is called.
- Error printing are also done through the terminal.

## Functions
- Functions have their own symbol table, so they can only access all the arugments that was passed to it. The symbol table of a function only contains all of its defined parameters.
- On a function call, it checks first if the number of passed arguments matches the number of parameter that the function requires. If so, it transfers the actual value of the argument into the symbol table of the function.
- It executes the function's statements by calling `execute_statement()` function with flags `FUNC_mode = True`.
- The symbol table of the actual function is also passed onto the `execute_statement()`, as well as the symbol of the parent function (the function in which the function was called). This allows for nesting of function calls.
- Returning from the function writes to the `parent_sym_table` arguments. This allows for multiple nested function calls.

## Switch-Case
- Since the language specification allows for a fallthrough, all of the statements of a switch-case were stored in a list, and the cases just contain the index of a statement in which the it will start executing.
> [!IMPORTANT]
> **Fallthrough**
> When a case in a switch statement does not have a break statement, execution "falls through" to the next case, executing the code for that case as well.
- Execution of statements will stop once a `GTFO` is encountered, or once it exhausted all of the statements in the statement list.
- A case will fallthrough the default case if the case above it does not have a `GTFO`.

### Description To-Do
- [ ] Functions Explanation
    - How it has its own symbol table
    - How it calls the `execute_statement` with different flags and arguments
    - How does it store the return value to the `IT` of the calling function using parent_sym_table.
- [ ] Switch case explanation
    - How it was implemented in a way such that fallthrough is supported.
    - How the cases do not contain the statements, but rather the index of which statement should they start executing.
- [ ] Siguro some UI integration

### Adding implementation for a statement:

- Add implementation to `execute_statement()` function.
- Implementation starts with checking the instance of the statement, use `isinstance(statement, <Statement Class>)` on an `if`-clause, and code the implementation in the body.
- Upon successful execution of the statement, always return `True`. If statement execution resulted in an error, return `False` instead.
- Check the class structure of the statement in the `/parser` folder to check the name of class attribute that holds the parameter/argument of the statement or other necessary tokens that is used in execution of the statement.
- Use `evaluate_expression(exr: Expression)` to evaluate expressions. It assumes that the arguments passed onto it is an instance of an `Expression` class so make sure that you are checking it first. You can use `isinstance(expr, Expression)` to check if an object is an expression.
- To modify a value to a symbol table, use `self.sym_table.modify_symbol(varident.lexeme, Symbol(<actual value>, <(Type.Yarn | Type.NUBMR | Type.NUMBAR | Type.TROOF | Type.NOOB)>))`. You can use `self.get_type()` if the type of the value can only be known on runtime, or if you are unsure of the type. It will be `self.sym_table.modify_symbol(varident.lexeme, Symbol(<actual value>, self.get_type(<actual value>)))`. Check first if `FUNC_mode` is true, if so, modify the passed `sym_table` instead.
- Methods of the symbol table can be found in the class declaration inside `symbol_table.py`.
- When retrieving value of a variable from the symbol table, it could return `None` if the variable is nonexistent. If it returned `None`, print an `Error.REFERENCED_UNDEFINED_VAR` using `self.printError(Errors.REFERENCED_UNDEFINED_VAR, statement.varident)`. Change the `TokenClass` argument accordingly.
- `self.retrieve_val(identifier: str)` accepts a variable name string. Name string could be attained from a `TokenClass` with a `token_type` of `TokenType.VARIDENT` using `<token class name>.lexeme`. It returns a `Symbol` object and to access its value, use its `value` attribute (`symbol.value`).
- Most statement involves modifying the symbol table.
- Input/Output is temporarily done in the python terminal, not in the `UI`. Modify `simple.lol` and run `test.py` to test the code.
- Most of the bugs ay nasa expression parser HAHAHAHAHABNA HIRAP XORI XORI
