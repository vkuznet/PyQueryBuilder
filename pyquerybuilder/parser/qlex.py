#!/usr/bin/env python
"""
perform parse on lexer
"""

import ply.lex as lex

tokens = [
   'GE',
   'LE',
   'NE',
   'GT',
   'LT',
   'EQUALS',
   'COMMA',
   'ID',
   'LB',
   'RB',
   'DATE',
   'QT'
]
reserved = {
   'find':'FIND',
   'where':'WHERE',
   'and':'AND',
   'or':'OR',
   'like':'LIKE',
   'not':'NOT',
   'count':'COUNT',
   'sum':'SUM',
   'min':'MIN',
   'max':'MAX',
}
tokens = tokens + list(reserved.values())
t_GE = r'\>='
t_LE = r'\<='
t_NE = r'\!='
t_GT = r'\>'
t_LT = r'\<'
t_EQUALS = r'\='
t_COMMA = r'\,'
t_LB = r'\('
t_RB = r'\)'
t_QT = r'\"'

def t_DATE(tok):
    r'\d{4}-\d{2}-\d{2}($|\s+\d{2}:\d{2}($|:\d{2}))'
    tok.type = 'DATE'
    return tok

def t_ID(tok):
#    r'[a-zA-Z_][a-zA-Z_0-9]*'
    r'[^\s><=!,()\"]+'
    tok.type = reserved.get(tok.value, 'ID')
    return tok


def t_newline(tok):
    r'\n+'
    tok.lexer.lineno += len(tok.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t\n\r\f\v'

def t_error(tok):

    print "Illegal character '%s'" % tok.value[0]
    # t.value attribute contains the rest of the input string 
    # that has not been tokenized.
    tok.lexer.skip(1)

LEXER = lex.lex(debug=0)

if __name__ == '__main__':
# Test it out
    DATA = '''find dataset where dataset like *Cosmic* '''
    DATA = '''find file, sum(block.size) where (dataset=*) '''
#    data = '''find file where file.createdate > 2010-01-01 \
#               and file.createdate < 2010-02-01 12:20 and \
#               file.createdate > 2010-02-01 12:30 CST and \
#               file.createdate < 2010-03-03 12:30:03 and  \
#               file.createdate > 2010-02-02 12:30:03 CST'''
#    data = '''find dataset, count(file), mix(block.size) \
#               where dateset like cosmic and (dataset.createdate>2010 \
#                or block.size > 200)'''
# Give the lexer some input
    LEXER.input(DATA)

# Tokenize
    while True:
        TOK = LEXER.token()
        if not TOK:
            break      # No more input
        print TOK

