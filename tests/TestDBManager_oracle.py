"""TestDBManger"""
import unittest
from pyquerybuilder.db.DBManager import DBManager

class TestDBManager(unittest.TestCase):
    """test DBManager"""
    def setUp(self):
        """default"""
        self.manager = DBManager()
        self.o_url = \
            'oracle://liangd:tiger@localhost.localdomain:1522/orcl:liangd'

    def test_get_dbname(self):
        """test execute query on sqlite DB"""
#       oracle
        arg = self.o_url
        db_name = self.manager.dbname(arg)
        print "db_name: %s" % db_name
        oracle_name = 'oracle-orcl-liangd |\#> '
        self.assertEqual(db_name, oracle_name)

    def test_connection(self):
        """test get connection with diff DB"""
#       oracle
        arg = self.o_url
        self.manager.connect(arg)
        self.manager.show_table('orcl-liangd')
        results = self.manager.execute("select count(*) from t1")
        rows = results.fetchall()
        self.manager.close('orcl-liangd')
        self.assertEqual(3, rows[0][0])

    def test_desc(self):
        """test describe database"""
#       oracle
        arg = self.o_url
        self.manager.connect(arg)
        length = self.manager.desc('orcl-liangd', 't1')
        self.assertEqual(4, length)
        length = self.manager.desc('orcl-liangd', 't2')
        self.assertEqual(4, length)
        self.manager.close('orcl-liangd')

    def test_dump(self):
        """test dump database in file"""
#       oracle
        arg = self.o_url
        self.manager.connect(arg)
        self.manager.dump('orcl-liangd')
        self.manager.close('orcl-liangd')

    def test_migrate_drop(self):
        """test migrate database"""
#       oracle
        arg = self.o_url
        self.manager.connect(arg)
        arg = 'oracle://scott:tiger@localhost.localdomain:1522/orcl:scott'
        self.manager.migrate('orcl-liangd', arg)
        self.manager.close('orcl-liangd')
        self.manager.connect(arg)
        
        results = self.manager.execute("select count(*) from t1")
        rows = results.fetchall()
        self.assertEqual(3, rows[0][0])
        
        self.manager.drop_table('orcl-scott', 't2')
        self.manager.drop_table('orcl-scott', 't1')
        self.manager.close('orcl-scott')

    def test_reconnect(self):
        """test reconnect to database"""
#       oracle
        arg = self.o_url
        self.manager.connect(arg)
        self.manager.reconnect('orcl-liangd')
        self.manager.close('orcl-liangd')

def suite():
    """suite of unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDBManager))
    return suite

#
# main
#
if __name__ == "__main__":

    unittest.TextTestRunner(verbosity=2).run(suite())

