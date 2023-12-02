'''
Parser Idea

Since ang goal is to analyze the program syntactically, meaning dapat in correct form yung program, irregardless of semantics
(sa next part yung semantics, for ex. isang error na pede maproduce ng semantics ay "variable referenced before declaration"),
need lang natin makapag buo ng parse tree based sa given tokens sa atin.

- Ang magiging input nung parser ay yung token list from lexers.
- Ang goal ng parser ay ma ensure na syntactically correct yung program, isang way para maensure yon is through creating a parse tree.
- Ang magiging output ng parser ay ang parse tree ng buong program.

Pano gagawa ng parse tree in code, specifically in python?
    - Through object, sila yung magiging nodes.

Ang naisip kong implementation is meron kang program object, tapos ang fields nya ay:
    - HAI -> TokenClass
    - VariableList -> ObjectNode (Similar to program)
    - Statement -> ObjectNode
    - KTHXBYE -> TokenClass

Breakdown ng fields:
    - HAI -> Sa HAI nag iistart ang lolcode program, if walang hi, mag eerror agad, expected HAI at line 1
    - VariableList -> If walang variable list, mag eerror ang program, variable list not found
    - Statement -> Can be empty ata HAHAHAHA
    - KTHXBYE -> Dito nag eend ang program, if wala mag eerror, expected KTHXBYE at line ...

Variable List Fields:
    - WAZZUP -> TokenClass
    - VariableDeclaration -> ObjectNode
    - BUHBYE -> TokenClass

VariableDeclaration Fields:
    - I HAS A -> TokenClass
    - varident -> TokenClass
    - ITZ -> TokenClass, optional
    - literal -> If may ITZ, dapat may literal

Statement Fields
    - Could either be:
        <print> | <input> | <expr> | <assignment> | <flow_control> | <global_assignment> | <typecast>
    - Statement -> ObjectNode
        -> Recursive to multiple statements

Pano makakapag buo ng parse tree given the tokenlist?
    - Since pinrocess natin yung tokenlist in an ordered way, meaning from start of code until end, walang modifications sa position,
    we can assume na yung chronological order nila is still the true representation of the code.

With that knowledge, pede tayong mag iterate through the token list.
While iterating, kelangan pa rin natin iuphold yung rules ng programming lang.
    Ex.
        First token should be HAI, followed by a variable list, then statement, then ang last token should be Code delimiter.

Cons ng approach na to:
    - Code representation is stored in one object (fragile HAHAHAHAA)
    - Di natin nacatch yung linebreak so mahihirapan tayo mag distinguish kung kelan mag tatapos ang statement at kung kelan mag start yung next (not so sure dito)

Di ko pa sure yung mismong interpretation HAHAHAHAHAAH
'''

class Expression():
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2