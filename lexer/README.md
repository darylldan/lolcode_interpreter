# Lexer

## Gist
- The whole `.lol` file is scanned and stored into a single string variable.
- The lexer conists of a buffer with operations:

    - **`consume()`** 
        - `consume()` removes the first character from the code stored in the string variable and appends it to the buffer.

    - **`consume_until_newline()`**
        - It repeatedly calls `consume()` until it encounters a newline. Newline is not consumed.

    - **`skip()`**
        - It removes the first character from the code stored in the string variable. It does not return anything.

    - **`peek()`**
        - Acts as a lookahead for the code. Returns the next character to be consumed, without removing it from the code.

    - **`peek_buffer()`**
        - Returns the most recent character added to buffer.

- The lexer consumes character until it encounters a whitespace, then it tries to match the buffer against all the defined regexes found in the values of the `TokenType` enum. If it finds a match, it adds it to the `token_list` field of the lexer.

- The lexer implementation in this project does more than just scanning, it also performs the following functions for the convenience of the syntax parser in the next stage.
    - Detects double whitespace (double whitespace between tokens is not allowed but trailing and leading whitespaces are allowed.)
    - Does not add comments as a token (both inline and multi-line).
    - Detects unterminated multi-line comment.
    - Detects if there is any character found after the multi-line comment delimiter (not allowed).

- Any unidentifed tokens were still scanned but stored with a token type of `TokenType.UNDEFINED`. Unterminated multi-line comments and unterminated strings are also stored with a token type of `TokenType.UNTERM_MULTILINE_COMMENT` and `TokenType.UNTERM_STR` respectively.

## Structure

### `lexer.py`

- Contains the main logic of the scanner.

### `token_class.py`

- Contains the class declaration for tokens. TokenClass containts the following attributes:

    - `token_type: TokenType` - Enum representation of the token.
    - `classification: str` - String description of the token.
    - `lexeme: str` - The content of the buffer when a regex match is found.
    - `literal: Any` - Actual value of a literal if a literal is matched.
    - `line: int` - Contains the line number where the token is scanned.
    - `error: Errors` - Only present in unidentified tokens. Used in error printing when token is parsed by the parser.
    - `error_context: TokenClass` - A class that can be used to better describe the error in the token.

### `token_type.py`

- Contains an enum representation of all the reserved words of the language (including identifiers and literals).
- The enums have their regex as a value, to be used by lexer to match what is in the buffer.
- Enums provide a type-safe way of checking what token is being parsed during the syntax analyzing phase compared to strings which is more prone to programming errors. It also allows auto complete when programming the interpreter.

## `token_classification.py`

- Contains all the description of a each token.
