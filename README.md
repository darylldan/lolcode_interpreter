# lolcode_interpreter

## Code status
- Testcases are now all working in parser (except dun sa mga testcases na may bug talaga).

## Test Cases Working

- [x] 1_variables
- [x] 2_gimmeh
- [x] 3_arith
- [ ] 4_smoosh_assign
- [ ] 5_bool
- [ ] 6_comparison
- [x] 7_ifelse
- [x] 8_switch
- [x] 9_loops
- [x] 10_functions

## Todo - Semantics
- ✅ Variable value evaluation
- ✅ Input Statement
- ✅ Output Statement
- ✅ Expression Parser - Daryll
    - ✅ Nesting Expression 
        - ✅ Addition
        - ✅ Subtraction
        - ✅ Multiplication
        - ✅ Division
        - ✅ Modulo
        - ✅ Min
        - ✅ Max
        - ✅ AND
        - ✅ OR
        - ✅ XOR
        - ✅ NOT
        - ✅ Equality (`==`) - Daryll
        - ✅ Inequality (`!=`) - Daryll
    - ✅ Infinite Arity Expression
        - ✅ All - Daryll
        - ✅ Any - Daryll
        - ✅ String Concatenation - Daryll
- [ ] Typecasting (Two methods) - France
- [ ] Assignment Statement - France
- ✅  If-Then Statement - France
- ✅ Switch-Case Statement (Invloves terminator/break/`GTFO`) - Daryll (wacky implementation nito HAHAHAAH)
- ✅  Loops (Invloves terminator/break/`GTFO`)
- ✅ Functions (Invloves terminator/break/`GTFO` and return statement `FOUND YR`) - Daryll

## Easily Implementable Bonuses
- [ ] Special character in yarn
- [ ] Suppress newline of output by ending visible statememnt with a `!`

## Todo
- Clean up debug print statements
- Check every usage of `self.is_literal` in parser, there must be a string delimiter case catcher everytime the said function is called.
- Gawing darkmode yung terminal HAHAHAHA
- Have a flag that will tell the semantic analyzer na wag na mag proceed pag nag error na yung sa parser.


## Bugs on Testcases
- Visible arguments are separated by `AN` instead of `+` (Test Case 4)
- Visible arguments are separated by `,` instead of `+` (Test Case 5)
- User input, which is string, is being compared into an int without typecasting (unless intentional) (Test Case 7).
- Case 0 do not have a break statement, if intentional it will fallthrough to the default case (Test Case 8)
- Visible arguments do not have a separator (should be `+`) (Test Case 8)
- Used 'PRODUCKT' instead of 'PRODUKT', resulting into an unidentified keyword error (Test Case 8)
- Case literals are integer but choice (from user input) is string. Either intentional or choice must be casted to integer, or case literal must be string.
- Function parameters are not separated by `YR` and `AN YR` (Test Case 10)
- Operands of arithmetic operations SUM OF are separated by `an` instead of `AN`. Parser detects it as varident (Test Case 10)
- Referenced an undefined variable `x` in function call to `printNum` (Test Case 10)