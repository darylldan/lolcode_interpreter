

#Sources:
#https://www.tutorialspoint.com/how-to-make-the-tkinter-text-widget-read-only#:~:text=In%20Tkinter%2C%20sometimes%2C%20we%20may,will%20make%20it%20read%2Donly.

#Import libraries
import tkinter  as tk 
from tkinter import * 
from tkinter import NS, Canvas, Scrollbar, ttk, filedialog, messagebox
import os
import re

#Global Variables
code = list()

lex_words = dict()
sym_words = dict()

no_of_lex = 0
no_of_sym = 0

lex_keys = []
sym_keys = [] 

lex_count = 0
sym_count = 0

selected_file = False

def load_buffer(name):
    with open(name, 'r') as arq:
        lines = arq.readlines()

    filtered_lines = []
    in_comment_block = False

    for line in lines:
        if 'OBTW' in line:
            in_comment_block = True
        elif 'TLDR' in line:
            in_comment_block = False
        elif not in_comment_block and 'BTW' not in line:
            filtered_lines.append(line.strip())
        elif not in_comment_block and 'BTW' in line:
            words_before_btw = line.split('BTW')[0].strip()
            if words_before_btw:
                filtered_lines.append(words_before_btw)
                
    return filtered_lines

def tokenize(code):
	rules = [
		('HAI', r'HAI'),
		('KTHXBYE', r'KTHXBYE'),
		('WAZZUP', r'WAZZUP'),
		('BUHBYE', r'BUHBYE'),
		('BTW', r'BTW'),
		('OBTW', r'OBTW'),
		('TLDR', r'TLDR'),
		('I_HAS_A', r'I HAS A'),
		('AN', r'AN'),
		('ITZ', r'ITZ'),
		('R', r'R'),
		('SUM_OF', r'SUM OF'),
		('DIFF_OF', r'DIFF OF'),
		('PRODUKT_OF', r'PRODUKT OF'),
		('QUOSHUNT_OF', r'QUOSHUNT OF'),
		('MOD_OF', r'MOD OF'),
		('BIGGR_OF', r'BIGGR OF'),
		('SMALLR_OF', r'SMALLR OF'),
		('BOTH_OF', r'BOTH OF'),
		('EITHER_OF', r'EITHER OF'),
		('WON_OF', r'WON OF'),
		('NOT', r'NOT'),
		('ANY_OF', r'ANY OF'),
		('ALL_OF', r'ALL OF'),
		('BOTH_SAEM', r'BOTH SAEM'),
		('DIFFRINT', r'DIFFRINT'),
		('SMOOSH', r'SMOOSH'),
		('MAEK', r'MAEK'),
		('A', r'A'),
		('IS_NOW_A', r'IS NOW A'),
		('VISIBLE', r'VISIBLE'),
		('GIMMEH', r'GIMMEH'),
		('O_RLY', r'O RLY\?'),
		('YA_RLY', r'YA RLY'),
		('MEBBE', r'MEBBE'),
		('NO_WAI', r'NO WAI'),
		('OIC', r'OIC'),
		('WTF', r'WTF\?'),
		('OMG', r'OMG'),
		('OMGWTF', r'OMGWTF'),
		('IM_IN_YR', r'IM IN YR'),
		('UPPIN', r'UPPIN'),
		('NERFIN', r'NERFIN'),
		('YR', r'YR'),
		('TIL', r'TIL'),
		('WILE', r'WILE'),
		('IM_OUTTA_YR', r'IM OUTTA YR'),
		('HOW_IZ_I', r'HOW IZ I'),
		('IF_U_SAY_SO', r'IF U SAY SO'),
		('GTFO', r'GTFO'),
		('FOUND_YR', r'FOUND YR'),
		('I_IZ', r'I IZ'),
		('MKAY', r'MKAY'),
		('NUMBR', r'-?[0-9]+'),
		('NUMBAR', r'-?[1-9]+\.[0-9]+'),
		('YARN', r'".*"'),
		('TROOF', r'(WIN|FAIL)'),
		('TYPE', r'(NUMBR|NUMBAR|YARN|TROOF|NOOB)'),
		('VAR_ID', r'[A-Za-z_][A-Za-z0-9_]*',),
		('QUOTES', r'"')
	]

	tokens_join = '|'.join('(?P<%s>%s)' % x for x in rules)
	lin_start = 0

	token = []
	lexeme = []

	for m in re.finditer(tokens_join, code):
		token_type = m.lastgroup
		token_lexeme = m.group(token_type)

		print(token_type)
		if token_type == 'NEWLINE':
			lin_start = m.end()
			lin_num += 1
		elif token_type == 'SKIP':
			continue
		elif token_type == 'MISMATCH':
			raise RuntimeError('%r unexpected on line %d' % (token_lexeme, lin_num))
		else:
			token.append(token_type)
   
		if token_lexeme.startswith('"') and token_lexeme.endswith('"'):
			lexeme.extend(['"', token_lexeme[1:-1], '"'])

			for substring in ['"', token_lexeme[1:-1], '"']:
				if substring == '"':
					lex_class = classify(substring)
					lex_words[substring] = lex_class
					lex_keys.append(substring)
				else:
					lex_words[substring] = 'Literal'
					lex_keys.append(substring)
		else:
			lexeme.append(token_lexeme)

			lex_class = classify(token_lexeme)
			lex_words[token_lexeme] = lex_class
			lex_keys.append(token_lexeme)

		print('Token = {0}, Lexeme = \'{1}\''.format(token_type, token_lexeme))
   
	return token, lexeme

def classify(lexeme):
	if lexeme in ['HAI', 'KTHXBYE']:
		return 'Code Delimiter'
	elif lexeme == 'I HAS A':
		return 'Variable Declaration'
	elif lexeme == 'ITZ':
		return 'Variable Assignment (following I HAS A)'
	elif lexeme == 'VISIBLE':
		return 'Output Keyword'
	elif lexeme == 'BTW':
		return 'Single-line Comment'
	elif lexeme == 'OBTW':
		return 'Multi-line Comment Delimiter'
	elif lexeme == 'TLDR':
		return 'Multi-line Comment Delimiter'
	elif lexeme in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
		return 'Arithmetic Operator'
	elif lexeme in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
		return 'Boolean Operator'
	elif lexeme in ['BOTH SAEM', 'DIFFRINT', 'SMALLR OF', 'BIGGR OF']:
		return 'Comparison Operator'
	elif lexeme == 'MKAY':
		return 'Variable Arity Delimiter'
	elif lexeme == 'SMOOSH':
		return 'Concatenation Operator'
	elif lexeme == 'MAEK':
		return 'Casting Operator'
	elif lexeme == 'IS NOW A':
		return 'Casting Operator / Variable Reassignment'
	elif lexeme == 'GIMMEH':
		return 'Input Keyword'
	elif lexeme == 'O RLY?':
		return 'If-Else Block Delimiter'
	elif lexeme == 'YA RLY':
		return 'If Statement'
	elif lexeme == 'NO WAI':
		return 'Else Statement'
	elif lexeme == 'MEBBE':
		return 'Else-if Statement'
	elif lexeme == 'OIC':
		return 'Conditional Block / Case Block Closer'
	elif lexeme == 'WTF?':
		return 'Switch Block Delimiter'
	elif lexeme == 'OMG':
		return 'Switch Case'
	elif lexeme == 'OMGWTF':
		return 'Default Switch Case'
	elif lexeme in ['IM IN YR', 'IM OUTTA YR']:
		return 'Loop Block Delimiter'
	elif lexeme == 'UPPIN':
		return 'Increment Keyword'
	elif lexeme == 'NERFIN':
		return 'Decrement Keyword'
	elif lexeme == 'YR':
		return 'Loop Variable Assignment'
	elif lexeme == 'TIL':
		return 'Until Loop Keyword'
	elif lexeme == 'WILE':
		return 'While Loop Keyword'
	elif lexeme in ['HOW IZ I', 'IF U SAY SO']:
		return 'Function Delimiter'
	elif lexeme == 'GTFO':
		return 'Break / Return Statement (without value / NOOB)'
	elif lexeme == 'FOUND YR':
		return 'Return Statement (with value)'
	elif lexeme == 'I IZ':
		return 'Function Caller'
	elif lexeme == 'AN':
		return 'Argument separator'
	elif lexeme == 'R':
		return 'Variable Assignment (without I HAS A)'
	elif lexeme == 'A':
		return 'Separator'
	elif re.match(r'(-?[0-9]+)', lexeme) or re.match(r'(-?[1-9]+\.[0-9]+)', lexeme) or re.match(r'".*"', lexeme) or re.match(r'(WIN|FAIL)', lexeme) or re.match(r'(NUMBR|NUMBAR|YARN|TROOF|NOOB)', lexeme):
		return 'Literal'
	elif lexeme == '"':
		return 'String Delimeter'
	elif re.match(r'[A-Za-z_][A-Za-z0-9_]*', lexeme):
		return 'Variable/Loop/Function Identifier'

#Choose file
def choose_file(code_text):
	global code

	global lex_words
	global sym_words

	global no_of_lex
	global no_of_sym

	global lex_keys
	global sym_keys

	global lex_count
	global sym_count

	global selected_file

	lex_words = dict()
	lex_keys = []
	no_of_lex = 0
	lex_count = 0

	sym_words = dict()
	sym_keys = []
	no_of_sym = 0
	sym_count = 0

    #Limit it to .lol files
	name = filedialog.askopenfilename(filetypes=[("LOL files", "*.lol")])

	if name:
		selected_file = True

		#Get lines of the selected file
		with open(name, "r") as f:
			code = f.readlines()
        
		for i in range(len(code)):
			code[i] = code[i].strip()

		code_text.config(state = "normal")
		code_text.delete("1.0", tk.END)

		for i in range(len(code)-1):
			code[i] = code[i].strip()
			code_text.insert(tk.END, "{} {}\n".format(str(i+1).ljust(5), code[i]))

		code[len(code)-1] = code[len(code)-1].strip()

		code_text.insert(tk.END, "{} {}\n".format(str(len(code)).ljust(5), code[len(code)-1]))

		# code_text.insert(tk.END, "Hi")
		# code_text.insert(tk.END, "\n".join(code))
		code_text.config(state = "disabled")
		# print("\n".join(code))
		# print(code)

		token = []
		lexeme = []

		for i in load_buffer(name):
			t, lex = tokenize(i)
			token += t
			lexeme += lex
		
		print(token)
		print(lexeme)

		populate_table(lexemetv["tree"], symboltv["tree"])

def populate_table(lex, sym):
	for item in lex.get_children():
		lex.delete(item)

	for item in sym.get_children():
		sym.delete(item)

	global lex_words
	global sym_words

	#Number of unique lexemes and symbols
	global no_of_lex
	global no_of_sym

	global lex_keys
	global sym_keys

	#Number of lexemes and symbols
	global lex_count
	global sym_count

	for i in range(len(lex_keys)):
		data = []
		data.append(lex_keys[i])
		data.append(lex_words[lex_keys[i]])
		lex.insert('','end', text="", values=tuple(data))

	for i in range(len(sym_keys)):
		data = []
		data.append(sym_keys[i])
		data.append(sym_words[sym_keys[i]])
		sym.insert('','end', text="", values=tuple(data))
    
	return lex, sym

def create_word_table(container, kind):
	canvas = tk.Canvas(container)
	yscrollbar = ttk.Scrollbar(canvas, orient="vertical")
	tree = ttk.Treeview(canvas, yscrollcommand=yscrollbar.set, column=("c1", "c2"), height=15)
	tree.grid(row=0, column=0, rowspan=15, columnspan=2)

	tree.column("#0",width=0, stretch=NO)
	tree.column("c1",width=100, anchor=tk.CENTER)
	tree.column("c2",width=200, anchor=tk.CENTER)
    
	tree.columnconfigure(0, weight=1)
	tree.columnconfigure(1, weight=1)
	tree.columnconfigure(2, weight=2)

	style = ttk.Style()
	style.theme_use("clam")
	style.configure("Treeview.Heading", font = ("Comfortaa", 10, "bold"), fill = 'gray')
    	
	if kind == "Lex":
		tree.heading("c1",text='Lexeme')
		tree.heading("c2",text='Classification')
	elif kind == "Sym":
		tree.heading("c1",text='Identifier')
		tree.heading("c2",text='Value')

    # tree = populate_table(tree)

	yscrollbar.configure(command=tree.yview)
	yscrollbar.grid(row=0, column=8, rowspan=15, sticky=NS)

	return {"canvas": canvas, "tree": tree}

LOLInterpreter = tk.Tk()
# LOLInterpreter.geometry("400x420")
LOLInterpreter.title("LHAHAHAHAHAHA") 
# LOLInterpreter.resizable(0,0)

container = tk.Frame(LOLInterpreter, bg = 'lightgrey')
container.pack(side="top", fill="both", expand=True)

top = tk.Frame(container, bg = 'lightgrey')
top.pack(side="top", fill="x", pady = 5)

left = tk.Frame(top, bg = 'lightgrey')
left.pack(side="left", fill="x", padx = 5)

code_text = tk.Text(left, state='disabled', height = 20, width = 50, font = ("Comfortaa", 12))
right = tk.Frame(top, bg = 'lightgrey')
table = tk.Frame(right, bg = 'lightgrey')
lexemetv = create_word_table(table, "Lex")
symboltv = create_word_table(table, "Sym")

file_button = Button(left, text="Choose File", command = lambda: choose_file(code_text), font = ("Glorieta", 12), bg = 'gray', fg = 'white')
file_button.pack(side = 'top', fill = "x", padx = (5, 0), pady = (5, 5))

code_text.pack(side = "top", fill="both", pady = (5, 5), padx = (5, 0))

right.pack(side="left", fill="x", padx = (5, 5))

title = tk.Label(right, text="LOL CODE INTERPRETER", font = ("Comfortaa", 12))
title.pack(side = "top", fill="x", pady = (5, 5), padx = (5, 5))

ttitle = tk.Frame(right, bg = 'lightgrey')
ttitle.pack(side="top", fill="x", padx = (5, 0), pady = (0, 0))

ltitle = tk.Label(ttitle, width = 34, text="Lexemes", font = ("Comfortaa", 12))
ltitle.pack(side = "left", fill="x", pady = (5, 5), padx = (3, 7))

stitle = tk.Label(ttitle, width = 34, text="Symbols", font = ("Comfortaa", 12))
stitle.pack(side = "left", fill="x", pady = (5, 5), padx = (9, 3))

table.pack(side="top", fill="x", padx = (5, 0))

lexemetv["canvas"].pack(side="left", pady=(5, 0), padx = (0, 5))
symboltv["canvas"].pack(side="left", pady=(5, 0), padx = (5, 5))

bot = tk.Frame(container, bg = 'lightgrey')
bot.pack(side="top", fill="x", pady = (0, 5))

exe_button = Button(bot, text="Execute", command = "", font = ("Glorieta", 12), bg = 'gray', fg = 'white')
exe_button.pack(side = 'top', fill = "x", padx = 5, pady = (0, 5))

console = tk.Text(bot, font = ("Comfortaa", 12), state='disabled')
console.pack(side = "top", fill = "x", pady = (5, 5), padx = (5, 5))

LOLInterpreter.mainloop()