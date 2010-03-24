"""TestDBManger"""
import unittest
from pyquerybuilder.db.DBManager import DBManager

class TestDBManager(unittest.TestCase):
    """test DBManager"""
    def setUp(self):
        """default"""
        self.manager = DBManager()

    def test_get_dbname(self):
        """test execute query on sqlite DB"""
#       sqlite
        db_name = self.manager.dbname('sqlite://test.db')
#        print "db_name: %s" % db_name
        sqlite_name = 'sqlite-test.db |\#> '
        self.assertEqual(db_name, sqlite_name)

    def test_connection(self):
        """test get connection with diff DB"""
#       sqlite
        self.manager.connect('sqlite://test.db')
        self.manager.show_table('test.db-sqlite')
        results = self.manager.execute("select count(*) from t1")
        rows = results.fetchall()
        self.manager.close('test.db-sqlite')
        self.assertEqual(3, rows[0][0])
        rows = []

    def test_desc(self):
        """test describe database"""
#       sqlite
        self.manager.connect('sqlite://test.db')
        length = self.manager.desc('test.db-sqlite', 't1')
        self.assertEqual(4, length)
        length = self.manager.desc('test.db-sqlite', 't2')
        self.assertEqual(4, length)
        self.manager.close('test.db-sqlite')

    def test_dump(self):
        """test dump database in file"""
#       sqlite
        self.manager.connect('sqlite://test.db')
        self.manager.dump('test.db-sqlite')
        self.manager.close('test.db-sqlite')

    def test_migrate_drop(self):
        """test migrate database"""
#       sqlite
        self.manager.connect('sqlite://migrate.db')
        self.manager.drop_db('migrate.db-sqlite')
        self.manager.close('migrate.db-sqlite')

        self.manager.connect('sqlite://test.db')
        self.manager.migrate('test.db-sqlite', 'sqlite://migrate.db')
        self.manager.close('test.db-sqlite')
        self.manager.connect('sqlite://migrate.db')

        results = self.manager.execute("select count(*) from t1")
        rows = results.fetchall()
        self.assertEqual(3, rows[0][0])
        rows = []

        self.manager.drop_table('migrate.db-sqlite', 't2')
        self.manager.drop_db('migrate.db-sqlite')
        self.manager.close('migrate.db-sqlite')

    def test_reconnect(self):
        """test reconnect to database"""
#       sqlite
        self.manager.connect('sqlite://test.db')
        self.manager.reconnect('test.db-sqlite')
        self.manager.close('test.db-sqlite')

def suite():
    """suite of unittest"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDBManager))
    return suite

#
# main
#
if __name__ == "__main__":

    unittest.TextTestRunner(verbosity=1).run(suite())

