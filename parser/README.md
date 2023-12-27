# Parser

## Gist

- The parser leverages the fact that the lexer produced a list of tokens that maintained the same order as the source code. It finds a grammar that matches the first token, and expects a series of token that the matched grammar requires. The lines of the tokens were also stored, as each token was encapsulated in a class called `TokenClass` which can be used to check if a series of statements belong to the same line.

- The inspiration for the parser is similar to those exercise problems in CMSC 141, where, for example, a language expects only two consecutive `x`'s. So, you have two states that check if the input string is `xx`. If it fails, then it goes to a dead state. In this parser implementation, if an unexpected token was encountered, it throws an error and stops the parsing.

## Structure

```
parser
├── assignment.py
│   ├── [Class] AssignmentStatement
│   └── [Class] ImplicitITAssignment
│
├── expression.py
│   ├── [Class | Parent] Expression
│   ├── [Class] BooleanExpression
│   ├── [Class] AnyOfExpression
│   ├── [Class] AllOfExpression
│   ├── [Class] ArithmeticExpression
│   ├── [Class] ComparisonExpression
│   └── [Class] String Concatination
│
├── flow_control.py
│   ├── [Class | Parent] FlowControl
│   ├── [Class] IfElseStatement
│   ├── [Class] SwitchCaseCase
│   ├── [Class] SwitchCaseDefault
│   ├── [Class] SwitchCaseStatement
│   ├── [Class] LoopCondition
│   ├── [Class] LoopStatement
│   └── [Class] Terminator
│
├── function_table.py
│   └── [Class] FunctionTable
│
├── functions.py
│   ├── [Class] FunctionStatement
│   ├── [Class] FunctionCallStatement
│   └── [Class] FunctionReturn
│
├── io.py
│   ├── [Class] InputStatement
│   └── [Class] PrintStatement
│
├── program.py
│   └── [Class] Program
│
├── statement.py
│   └── [Class | Parent] Statement
│
├── typecast.py
│   ├── [Class] TypecastStatement
│   └── [Class] RecastStatement
│
├── variable_declaration.py
│   └── [Class] VariableDeclaration
│
└── variable_list.py
    └── [Class] VariableList
```

- The files `assignment.py`, `expression.py`, `flow_control.py`, `functions.py`, `io.py`, `statement.py`, `variable_declaration.py`, and `typecast.py` contain class declarations for their respective features. Each class contains all the necessary tokens needed for its feature, such as the argument list for the features that require it, or the source and destination tokens for assignment statements. It also serves as the grammar holder of statements as each class requires specific tokens to be declared.
- The files `function_table.py`, `program.py`, and `variable_list.py` contains class declarations for utilities that will be used during the parsing stage.
    
    - `FunctionTable`
        - Contains a dictionary of all the functions that was declared in the code. The function identifier serves as the key while its value is a `FunctionStatement` class which contains all the formal parameters and the list of statements to be executed.
    - `program.py`
        - This class serves as the object representation of the whole lolcode program. It contains all the variable declarations statements, a function table, and all the statements to be executed in the program.
        - This is the class that the semantic analyzer accepts.
    - `variable_list.py`
        - This contains all the variable declaration, including their initialization if present, of the lolcode program. It is convenient to store them in a separate list since they are all declared in the same section.

- The main logic for the parser is stored in the `parser.py` file.


## Class Structure

- There is a grand parent class called `Statement` which most classes declared in this module inherit from.
- The direct subclasses of `Statement` are:
    - `AssignmentStatement`
    - `ImplicitITAssignment`
    - `Expression`
    - `FlowControl`
    - `FunctionStatement`
    - `FunctionCallStatement`
    - `FunctionReturn`
    - `InputStatement`
    - `PrintStatement`
    - `TypecastStatement`
    - `RecastStatement`
- Expression is the parent class for all the expression statement. This is very useful in semantics part as you only have to check if a statement is expression instead of comparing it against individual expressions.
- FlowControl is the parent class for all the statements that modify the flow of the program, except functions.

## Expression Parser

### Nesting Expresssions

- Since all expressions are in prefix form, they can be utilized to check their validity.
- A prefix expression is valid only if the number of operands is equal to the number of operators plus one.
- All parameters are separated by `AN`. Thus, a counter for the required `AN`s was tracked during expression parsing.
- As expressions can be nested (except for some), the counter for the required operands was also implemented.
- If the starting operation is not `NOT`, the `an_counter` and `op_counter` start at `1` and `2`, respectively. However, if the starting operation is `NOT`, then `an_counter` and `op_counter` start at `0` and `1`, respectively. When the parser encounters another operator as an operand, it decreases `op_counter` by `1`. Subsequently, it increases it by `2`, signifying the addition of another operation, thereby requiring two more operands. However, as the operation itself is an operand to the previous operation, it decreases by one. Essentially, encountering an operator increments `op_counter` by `1`, except for the `NOT` operator, which essentially increments the counter by `1` and decrements it by `1`. Encountering an operand (literal or varident) decrements `op_counter` by `1`. Additionally, `an_counter` is incremented every time the parser encounters an operator and decremented every time it encounters the `AN` keyword.
- At the end of parsing, if both the `op_counter` and `an_counter` are not equal to zero, an `Incomplete Expression` error is thrown. This approach's downside is the inability to specify the erroneous token in the expression; it merely indicates that the expression is incorrect.
- As expressions can also be used inline with arguments, a flag called `NS_mode (nesting mode)` was implemented to check if the expression is valid when the next token is `AN` (separator for some statements) or `+` (separator for visible statements).
