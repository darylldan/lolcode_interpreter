# lolcode_interpreter

## Code status
- Interpreter now executes all the testcases without any bugs.
- Interpreter is done but needs more testing.

## Test Cases Working

- [x] 1_variables
- [x] 2_gimmeh
- [x] 3_arith
- [x] 4_smoosh_assign
- [x] 5_bool
- [x] 6_comparison
- [x] 7_ifelse
- [x] 8_switch
- [x] 9_loops
- [x] 10_functions

## Todo - UI
- [x] Integrate terminal
- [x] Once terminal is integrated, update the code accordingly (move print errors to ui terminal, as well as program input and output)
- [ ] Make it such that symbol table on UI is updated everytime symbol table is updated in interpreter - wag n 2
- [ ] Test if the text editor in UI is working.

## Todo - Documentation
- [x] Document the `semantics.py`
- [x] Finish overview documentation of semantics (`semantics/README.md`)

## Todo - Semantics [DONE]
- ✅ Variable value evaluation
- ✅ Input Statement
- ✅ Output Statement
- ✅ Expression Parser - Daryll
    - ✅ Nesting Expression 
        - ✅ Addition - Mark
        - ✅ Subtraction - Mark
        - ✅ Multiplication - Mark
        - ✅ Division - Mark
        - ✅ Modulo - Mark
        - ✅ Min - 
        - ✅ Max - 
        - ✅ AND - 
        - ✅ OR - 
        - ✅ XOR
        - ✅ NOT
        - ✅ Equality (`==`) - Daryll
        - ✅ Inequality (`!=`) - Daryll
    - ✅ Infinite Arity Expression
        - ✅ All - Daryll
        - ✅ Any - Daryll
        - ✅ String Concatenation - Daryll
- ✅ Typecasting (Two methods) - France
- ✅ Assignment Statement - France
- ✅  If-Then Statement - France
- ✅ Switch-Case Statement (Invloves terminator/break/`GTFO`) - Daryll (wacky implementation nito HAHAHAAH)
- ✅  Loops (Invloves terminator/break/`GTFO`)
- ✅ Functions (Invloves terminator/break/`GTFO` and return statement `FOUND YR`) - Daryll

## Easily Implementable Bonuses
- [x] Special character in yarn
- [ ] Suppress newline of output by ending visible statememnt with a `!` (tinatamad p aq sorry wahahaha pero it involves ammending yung lexer to accept `!`, then ammending yung parser to accept `!`, and to update the semantincs such that if `!` is present, no need to add newline. imomodify din yung ano, class structure ng visible if iimplement e2)

## Todo
- [ ] Clean up debug print statements
- [x] Check every usage of `self.is_literal` in parser, there must be a string delimiter case catcher everytime the said function is called.
- [ ] Gawing darkmode yung terminal HAHAHAHA - wag n e2
- [ ] Have a flag that will tell the semantic analyzer na wag na mag proceed pag nag error na yung sa parser.
- [ ]Make it such that symbol table in the UI is being updated everytime it is modified. - wag n e2


## Bugs on Testcases
- Visible arguments are separated by `AN` instead of `+` (Test Case 4)
- Visible arguments are separated by `,` instead of `+` (Test Case 5)
- Relational operations are yielding unexpected results because `BOTH SAEM` and `DIFFRINT` do not automatically cast operands. For instance, in line 24, if `x = 5` and `y = 7`, the expected result is `x <= y -> 5 <= 7 -> WIN`. However, `SMALLR OF` casts `x` and `y` from strings (as they originate from input or `GIMMEH`) to numbers. Therefore, when evaluating `5` and `'5'` (from the variable `x` which is a string because it came from user input) using the operation `BOTH SAEM`, the result is `FAIL`. Variables `x` and `y` must first be typecasted into numbers, unless the test case intentionally requires otherwise. (Test Case 6)
- User input, which is string, is being compared into an int without typecasting (unless intentional) (Test Case 7).
- Case 0 do not have a break statement, if intentional it will fallthrough to the default case (Test Case 8)
- Visible arguments do not have a separator (should be `+`) (Test Case 8)
- Used 'PRODUCKT' instead of 'PRODUKT', resulting into an unidentified keyword error (Test Case 8)
- Case literals are integer but choice (from user input) is string. Either intentional or choice must be casted to integer, or case literal must be string.
- Function parameters are not separated by `YR` and `AN YR` (Test Case 10)
- Operands of arithmetic operations SUM OF are separated by `an` instead of `AN`. Parser detects it as varident (Test Case 10)
- Referenced an undefined variable `x` in function call to `printNum` (Test Case 10)
