#!/usr/bin/env python
"""
Test Utils
"""

import unittest
from pyquerybuilder.utils.Utils import similar

class TestUtils(unittest.TestCase):
    """unittest for Utils"""
    def setUp(self):
        """ initial"""
        pass
    def test_similar(self):
        """ test similar fuction for attribute link looking up"""
        attr = 'type'
        column = 'dataset_access_types'
        self.assertEqual(True, similar(attr, column))
        attr = 'createdate'
        column = 'CreationDate'
        self.assertEqual(True, similar(attr, column))
        attr = 'moddate'
        column = 'LastModificationDate'
        self.assertEqual(True, similar(attr, column))


def suite():
    """suite of unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite

#
# main
#
if __name__ == "__main__":

    unittest.TextTestRunner(verbosity=2).run(suite())

