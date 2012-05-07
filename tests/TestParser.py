#!/usr/bin/env python
"""
Test mapper object
"""

import unittest
from pyquerybuilder.parser import qparse

class TestParser(unittest.TestCase):
    """Test Mapper class"""
    def setUp(self):
        """ auto init"""
        self.parser = qparse

    def test_correct_inputs(self):
        """test correct query"""
        inputs = [ 
          'find dataset',
          'find a where a > 1',
          'find ab where a>1',
          'find ac where a>1 and (b>2)',
          'find asc where a>2 and (a>1 and b <3)',
          'find a.b,c where a.c >2 and f>1 or file<3',
          'find a,b.c,c where a>2 and (b<1 or( c>2 and b<3)and e.c<2) or e<1',
          'find a where b > "C "',
          'find a where b >" B   C" ',
          'find asc where a>"2" and (a>"1" and b < " 3 ")',
        ]
        result = []  
        for line in inputs:
            result.append(self.parser.parse(line))
        self.assertTrue(result[0]['keywords'][0] == ['dataset'])
        self.assertTrue(result[1]['constraints'][0]['value'] == '1')
        self.assertTrue(result[2]['constraints'][0]['value'] == '1')
        self.assertTrue(result[3]['constraints'][1] == 'and')
        self.assertTrue(result[4]['constraints'][2][2]['sign'] == '<')
        self.assertTrue(result[5]['keywords'][0] == ['a.b'])
        self.assertTrue(result[6]['constraints'][2][2][2]['value'] == '3')
        self.assertTrue(result[7]['constraints'][0]['value'] == 'C')
        self.assertTrue(result[8]['constraints'][0]['value'] == 'B C')
        self.assertTrue(result[4]['constraints'][2][2]['value'] == '3')

    def test_wrong_inputs(self):
        """test wrong query"""
        inputs = [
          'find dataset whe',
          'find a where a>',
          'find ac where a>1 (and b>2',
          'find ac where a>1 and b<2)',
          'find asc, where a>2',
          'find a where a > "C',
        ]
        for line in inputs:
            self.assertTrue( None == self.parser.parse(line))

def suite():
    """suite of unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestParser))
    return suite

#
# main
#
if __name__ == "__main__":

    unittest.TextTestRunner(verbosity=2).run(suite())

