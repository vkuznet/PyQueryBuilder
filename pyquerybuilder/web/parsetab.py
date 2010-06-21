
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = '\x0c\x1eS\xe8\n\x03\xeeq\x88?j\xb6c\xa7\xc66'
    
_lr_action_items = {'MIN':([3,15,16,22,39,40,],[6,6,6,6,6,6,]),'SUM':([3,15,16,22,39,40,],[8,8,8,8,8,8,]),'DATE':([31,32,33,34,35,36,38,55,],[43,43,43,43,43,43,43,43,]),'FIND':([0,],[3,]),'LE':([9,23,26,27,28,29,],[-6,36,-10,-8,-9,-7,]),'LB':([4,6,7,8,16,22,39,40,],[11,12,13,14,22,22,22,22,]),'NE':([9,23,26,27,28,29,],[-6,32,-10,-8,-9,-7,]),'LT':([9,23,26,27,28,29,],[-6,33,-10,-8,-9,-7,]),'COMMA':([5,9,10,21,26,27,28,29,],[-5,-6,15,-4,-10,-8,-9,-7,]),'RB':([17,18,19,20,24,30,41,42,43,44,45,46,47,48,49,50,51,52,53,54,56,57,58,59,60,61,62,],[26,27,28,29,-15,41,-32,-25,-11,-17,-29,-21,-27,-19,-28,-20,-24,-16,-26,-18,-30,-22,-13,-14,-12,-31,-23,]),'$end':([1,2,5,9,10,21,24,25,26,27,28,29,41,42,43,44,45,46,47,48,49,50,51,52,53,54,56,57,58,59,60,61,62,],[-3,0,-5,-6,-2,-4,-15,-1,-10,-8,-9,-7,-32,-25,-11,-17,-29,-21,-27,-19,-28,-20,-24,-16,-26,-18,-30,-22,-13,-14,-12,-31,-23,]),'COUNT':([3,15,16,22,39,40,],[4,4,4,4,4,4,]),'GT':([9,23,26,27,28,29,],[-6,31,-10,-8,-9,-7,]),'EQUALS':([9,23,26,27,28,29,],[-6,34,-10,-8,-9,-7,]),'GE':([9,23,26,27,28,29,],[-6,35,-10,-8,-9,-7,]),'WHERE':([5,9,10,21,26,27,28,29,],[-5,-6,16,-4,-10,-8,-9,-7,]),'ID':([3,11,12,13,14,15,16,22,31,32,33,34,35,36,38,39,40,43,55,],[9,17,18,19,20,9,9,9,44,46,48,50,52,54,57,9,9,60,62,]),'AND':([24,25,30,41,42,43,44,45,46,47,48,49,50,51,52,53,54,56,57,58,59,60,61,62,],[-15,39,39,-32,-25,-11,-17,-29,-21,-27,-19,-28,-20,-24,-16,-26,-18,-30,-22,-13,-14,-12,-31,-23,]),'LIKE':([9,23,26,27,28,29,37,],[-6,38,-10,-8,-9,-7,55,]),'MAX':([3,15,16,22,39,40,],[7,7,7,7,7,7,]),'error':([0,],[1,]),'NOT':([9,23,26,27,28,29,],[-6,37,-10,-8,-9,-7,]),'OR':([24,25,30,41,42,43,44,45,46,47,48,49,50,51,52,53,54,56,57,58,59,60,61,62,],[-15,40,40,-32,-25,-11,-17,-29,-21,-27,-19,-28,-20,-24,-16,-26,-18,-30,-22,-13,-14,-12,-31,-23,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'keyword':([3,15,16,22,39,40,],[5,21,23,23,23,23,]),'constraint':([16,22,39,40,],[24,24,58,59,]),'date':([31,32,33,34,35,36,38,55,],[42,45,47,49,51,53,56,61,]),'keywords':([3,],[10,]),'query':([0,],[2,]),'constraints':([16,22,],[25,30,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> query","S'",1,None,None,None),
  ('query -> FIND keywords WHERE constraints','query',4,'p_query','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',14),
  ('query -> FIND keywords','query',2,'p_query','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',15),
  ('query -> error','query',1,'p_query_error','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',24),
  ('keywords -> keywords COMMA keyword','keywords',3,'p_keywords','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',31),
  ('keywords -> keyword','keywords',1,'p_keywords','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',32),
  ('keyword -> ID','keyword',1,'p_keyword','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',40),
  ('keyword -> SUM LB ID RB','keyword',4,'p_keyword','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',41),
  ('keyword -> MIN LB ID RB','keyword',4,'p_keyword','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',42),
  ('keyword -> MAX LB ID RB','keyword',4,'p_keyword','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',43),
  ('keyword -> COUNT LB ID RB','keyword',4,'p_keyword','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',44),
  ('date -> DATE','date',1,'p_date','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',51),
  ('date -> DATE ID','date',2,'p_date','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',52),
  ('constraints -> constraints AND constraint','constraints',3,'p_constraints','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',59),
  ('constraints -> constraints OR constraint','constraints',3,'p_constraints','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',60),
  ('constraints -> constraint','constraints',1,'p_constraints','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',61),
  ('constraint -> keyword GE ID','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',73),
  ('constraint -> keyword GT ID','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',74),
  ('constraint -> keyword LE ID','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',75),
  ('constraint -> keyword LT ID','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',76),
  ('constraint -> keyword EQUALS ID','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',77),
  ('constraint -> keyword NE ID','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',78),
  ('constraint -> keyword LIKE ID','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',79),
  ('constraint -> keyword NOT LIKE ID','constraint',4,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',80),
  ('constraint -> keyword GE date','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',81),
  ('constraint -> keyword GT date','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',82),
  ('constraint -> keyword LE date','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',83),
  ('constraint -> keyword LT date','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',84),
  ('constraint -> keyword EQUALS date','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',85),
  ('constraint -> keyword NE date','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',86),
  ('constraint -> keyword LIKE date','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',87),
  ('constraint -> keyword NOT LIKE date','constraint',4,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',88),
  ('constraint -> LB constraints RB','constraint',3,'p_constraint','/data/Python/lib/python2.6/site-packages/PyQueryBuilder-1.0.0-py2.6.egg/pyquerybuilder/parser/qparse.py',89),
]
