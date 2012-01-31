#!/usr/bin/env python
"""
perform parse on syntax
"""

import ply.yacc as yacc
import qlex

tokens = qlex.tokens

# word
# find dataset where dataset like *word*
def p_query(pattern):
    '''query : FIND keywords WHERE constraints
           | FIND keywords'''
    pattern[0] = {}
    if len(pattern) <= 3 and pattern[1]:
        pattern[0]['keywords'] = pattern[2]
    elif len(pattern) > 3:
        pattern[0]['keywords'] = pattern[2]
        pattern[0]['constraints'] = pattern[4]

def p_query_error(pattern):
    '''query : error'''
    pattern[0] = None
    lexpos = 0
    print "format error at ", pattern[1]


def p_keywords(pattern):
    '''keywords : keywords COMMA keyword
                | keyword '''
    if len(pattern) > 2:
        pattern[0] = pattern[1]
        pattern[0].append(pattern[3])
    else:
        pattern[0] = [pattern[1]]

def p_keyword(pattern):
    '''keyword : ID
               | SUM LB ID RB
               | MIN LB ID RB
               | MAX LB ID RB
               | COUNT LB ID RB  '''
    if len(pattern) == 2:
        pattern[0] = [pattern[1]]
    elif len(pattern) == 5:
        pattern[0] = [pattern[3], pattern[1]]

def p_date(pattern):
    '''date : DATE
            | DATE ID'''
    if len(pattern) == 2:
        pattern[0] = pattern[1]
    elif len(pattern) == 3:
        pattern[0] = ' '.join(pattern[1:])

def p_constraints(pattern):
    '''constraints : constraints AND constraint
                   | constraints OR constraint
                   | constraint'''
    if len(pattern) == 4 :
        pattern[0] = pattern[1]
        pattern[0].append(pattern[2])
        pattern[0].append(pattern[3])
#    elif pattern[1] == 'LB':
#        pattern[0] = [ pattern[1] ]
    else:
        pattern[0] = [pattern[1]]


def p_constraint(pattern):
    '''constraint : keyword GE ID
                  | keyword GT ID
                  | keyword LE ID
                  | keyword LT ID
                  | keyword EQUALS ID
                  | keyword NE ID
                  | keyword LIKE ID
                  | keyword NOT LIKE ID
                  | keyword GE date
                  | keyword GT date
                  | keyword LE date
                  | keyword LT date
                  | keyword EQUALS date
                  | keyword NE date
                  | keyword LIKE date
                  | keyword NOT LIKE date
                  | LB constraints RB'''

    if pattern[1] == '(':
        pattern[0] = pattern[2]
    elif len(pattern) == 4 :
        pattern[0] = {}
        pattern[0]['keyword'] = pattern[1]
        pattern[0]['sign'] = pattern[2]
        pattern[0]['value'] = pattern[3]
    elif len(pattern) == 5 and pattern[2] == 'NOT' :
        pattern[0] = {}
        pattern[0]['keyword'] = pattern[1]
        pattern[0]['sign'] = pattern[2:4]
        pattern[0]['value'] = pattern[4]


#### Catastrophic error handler
def p_error(pattern):
    if not pattern:
        print("SYNTAX ERROR AT EOF")


QPARSER = yacc.yacc()

def parse(data, debug=0):
    """parse """
    QPARSER.error = 0
    result = QPARSER.parse(data, debug=debug)
    if QPARSER.error:
        return None
    return result

if __name__ == '__main__':
#    'lexer', 'lexpos', 'lineno', 'type', 'value'
#    sdata = """find dataset where dataset like cosmic"""
#    sdata = """find dataset where dataset like cosmic \
#            and dataset.createdate > 2010"""
#    sdata = """find dataset, count(file), max(block.size) \
#           where dateset like cosmic and \
#           (dataset.createdate>2010 or block.size > 200)"""

    while True:
        try:
            QUERY = raw_input('calc > ')
        except EOFError:
            break
        if not QUERY:
            continue
        RESULT = parse(QUERY)
        print RESULT

