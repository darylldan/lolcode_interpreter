from enum import Enum

class Errors(Enum):
    DOUBLE_WHITESPACE = 1
    UNTERM_STR = 2
    UNIDENT_KEYWORD = 3
    UNEXPECTED_CHAR_TLDR = 4
    UNTERM_MULTILINE_COMMENT = 5
    EXPECTED_HAI = 6
    EXPECTED_WAZZUP = 7
    EXPECTED_BUHBYE = 8
    EXPECTED_KTHXBYE = 9
    EXPECTED_IHASA = 10
    EXPECTED_VARIDENT = 11
    UNEXPECTED_NEWLINE = 12
    UNEXPECTED_TOKEN = 13
    INVALID_VAR_VALUE = 14
    UNEXPECTED_OPERAND = 15
    INVALID_STRING_CONT_ARG = 16
    INVALID_ARG_SEPARATOR = 17
    INCOMPLETE_EXPR = 18