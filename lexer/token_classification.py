import re

def classify(keyword):
    code_dictionary = {
        'HAI': 'Code Delimiter',
        'KTHXBYE': 'Code Delimiter',
        'BTW': 'Single-line Comment',
        'I HAS A': 'ITZ',
        'VISIBLE': 'Output Keyword',
        'OBTW': 'Multi-line Comment Delimiter',
        'TLDR': 'Multi-line Comment Delimiter',
        'I HAS A': 'Variable Declaration',
        'ITZ': 'Variable Assignment (following I HAS A)',
        'R': 'Variable Assignment (without I HAS A)',
        'SUM OF': 'Arithmetic Operator',
        'DIFF OF': 'Arithmetic Operator',
        'PRODUKT OF': 'Arithmetic Operator',
        'QUOSHUNT OF': 'Arithmetic Operator',
        'MOD OF': 'Arithmetic Operator',
        'BOTH OF': 'Boolean Operator',
        'EITHER OF': 'Boolean Operator',
        'WON OF': 'Boolean Operator',
        'NOT': 'Boolean Operator',
        'ANY OF': 'Boolean Operator',
        'ALL OF': 'Boolean Operator',
        'BOTH SAEM': 'Comparison Operator',
        'DIFFRINT': 'Comparison Operator',
        'BIGGR OF': 'Comparison Operator',
        'SMALLR OF': 'Comparison Operator',
        'SMOOSH': 'Concatenation Operator',
        'MAEK': 'Casting Operator',
        'A': 'Separator',
        'IS NOW A': 'Casting Operator / Variable Reassignment',
        'VISIBLE': 'Output Keyword',
        'GIMMEH': 'Input Keyword',
        'O RLY?': 'If-Else Block Delimiter',
        'YA RLY': 'If Statement',
        'MEBBE': 'Else-if Statement',
        'NO WAI': 'Else Statement',
        'OIC': 'Conditional Block / Case Block Closer',
        'WTF?': 'Switch Block Delimiter',
        'OMG': 'Switch Case',
        'OMGWTF': 'Default Switch Case',
        'IM IN YR': 'Loop Block Delimiter',
        'UPPIN': 'Increment Keyword',
        'NERFIN': 'Decrement Keyword',
        'YR': 'Loop Variable Assignment',
        'TIL': 'Until Loop Keyword',
        'WILE': 'While Loop Keyword',
        'IM OUTTA YR': 'Loop Block Delimiter',
        'HOW IZ I': 'Function Delimiter',
        'IF U SAY SO': 'Function Delimiter',
        'GTFO': 'Break OR Return Statement Without Value',
        'FOUND YR': 'Return Statement With Value',
        'I IZ': 'Function Caller',
        'MKAY': 'Variable Arity Delimiter',
        '"': 'String Delimiter',
        'WAZZUP': 'Variable List Delimiter',
        'BUHBYE': 'Variable List Delimiter',
        'VARIDENT': 'Variable Identifier',
        'WIN': 'Boolean Value (True)',
        'FAIL': 'Boolean Value (False)',
        'NUMBR': 'Integer Literal',
        'NUMBAR': 'Float Literal',
        'AN': 'Multiple Parameter Separator',
        '+': 'Visible Parameter Concatenator'
    }

    classOfKeyWord = code_dictionary[keyword]
    return classOfKeyWord
