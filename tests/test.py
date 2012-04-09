import unittest
import TestDBManager
import TestDB
import TestGraph
import TestConstructQuery
import TestQueryBuilder
import TestParser
import TestMapper
import TestSchema
import TestWGraph
import TestSchemaHandler

suite1 = TestDBManager.suite()
suite2 = TestDB.suite()
suite3 = TestGraph.suite()
suite31 = TestWGraph.suite()
suite4 = TestConstructQuery.suite()
suite41 = TestSchema.suite()
suite42 = TestSchemaHandler.suite()
suite5 = TestQueryBuilder.suite()
suite6 = TestParser.suite()
suite7 = TestMapper.suite()

Suite  = unittest.TestSuite()
Suite.addTest(suite1)
Suite.addTest(suite2)
Suite.addTest(suite3)
Suite.addTest(suite31)
Suite.addTest(suite4)
Suite.addTest(suite41)
Suite.addTest(suite42)
Suite.addTest(suite5)
Suite.addTest(suite6)
Suite.addTest(suite7)

unittest.TextTestRunner(verbosity=1).run(Suite)




