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
#       mysql
        db_name = self.manager.dbname('mysql://cms:passcms@localhost:3306/test')
#        print "db_name: %s" % db_name
        mysql_name = 'mysql-test-localhost |\#> '
        self.assertEqual(db_name, mysql_name)

    def test_connection(self):
        """test get connection with diff DB"""
#       mysql
        self.manager.connect('mysql://cms:passcms@localhost:3306/test')
        self.manager.show_table('test-mysql')
        results = self.manager.execute("select count(*) from t1")
        rows = results.fetchall()
        self.manager.close('test-mysql')
        self.assertEqual(3, rows[0][0])
        rows = []

    def test_desc(self):
        """test describe database"""

#       mysql
        self.manager.connect('mysql://cms:passcms@localhost:3306/test')
        length = self.manager.desc('test-mysql', 't1')
        self.assertEqual(4, length)
        length = self.manager.desc('test-mysql', 't2')
        self.assertEqual(4, length)
        self.manager.close('test-mysql')

    def test_dump(self):
        """test dump database in file"""

#       mysql
        self.manager.connect('mysql://cms:passcms@localhost:3306/test')
        self.manager.dump('test-mysql')
        self.manager.close('test-mysql')

    def test_migrate_drop(self):
        """test migrate database"""

#       mysql
        self.manager.connect('mysql://cms:passcms@localhost:3306/test')
        self.manager.migrate('test-mysql', \
               'mysql://cms:passcms@localhost:3306/migrate')
        self.manager.close('test-mysql')
        self.manager.connect('mysql://cms:passcms@localhost:3306/migrate')

        results = self.manager.execute("select count(*) from t1")
        rows = results.fetchall()
        self.assertEqual(3, rows[0][0])
        rows = []

        self.manager.drop_table('migrate-mysql', 't2')
        self.manager.drop_db('migrate-mysql')
        self.manager.close('migrate-mysql')

    def test_reconnect(self):
        """test reconnect to database"""

#       mysql
        self.manager.connect('mysql://cms:passcms@localhost:3306/test')
        self.manager.reconnect('test-mysql')
        self.manager.close('test-mysql')

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

