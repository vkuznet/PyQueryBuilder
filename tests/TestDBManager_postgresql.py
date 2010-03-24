"""TestDBManger"""
import unittest
from pyquerybuilder.db.DBManager import DBManager
#_DEBUG = True
#import traceback
class TestDBManager(unittest.TestCase):
    """test DBManager"""
    def setUp(self):
        """default"""
        self.manager = DBManager()
        self.p_url = 'postgresql://liangd:tiger@localhost:5432/test'

    def test_get_dbname(self):
        """test execute query on sqlite DB"""
#       postgresql
        arg = self.p_url
        db_name = self.manager.dbname(arg)
        print "db_name: %s" % db_name
        postgresql_name = 'postgresql-test-localhost |\#> '
        self.assertEqual(db_name, postgresql_name)

    def test_connection(self):
        """test get connection with diff DB"""
#       postgresql
        arg = self.p_url
        self.manager.connect(arg)
        self.manager.show_table('test-postgresql')
        results = self.manager.execute("select count(*) from t1")
        rows = results.fetchall()
        self.manager.close('test-postgresql')
        self.assertEqual(3, rows[0][0])

    def test_desc(self):
        """test describe database"""
#       postgresql
        arg = self.p_url 
        self.manager.connect(arg)
        length = self.manager.desc('test-postgresql', 't1')
        self.assertEqual(4, length)
        length = self.manager.desc('test-postgresql', 't2')
        self.assertEqual(4, length)
        self.manager.close('test-postgresql')

    def test_dump(self):
        """test dump database in file"""
#       postgresql
        arg = self.p_url
        self.manager.connect(arg)
        self.manager.dump('test-postgresql')
        self.manager.close('test-postgresql')

    def test_migrate_drop(self):
        """test migrate database"""
#       postgresql
        self.manager.connect(self.p_url)
        arg = 'postgresql://liangd:tiger@localhost:5432/migrate'
        self.manager.migrate('test-postgresql', arg)
        self.manager.close('test-postgresql')
        print "finished migrated and closed test-postgresql DB"

        self.manager.connect(arg)
        results = self.manager.execute("select count(*) from t1")
        rows = results.fetchall()
        self.assertEqual(3, rows[0][0])
        rows = []
        self.manager.close('migrate-postgresql')
        self.manager.connect(arg)


#        if _DEBUG == True:
#            import pdb
#            pdb.set_trace()      
#        try:
#            self.manager.drop_table('migrate-postgresql', 't2')
#            self.manager.drop_table('migrate-postgresql', 't1')

#        except:
#            traceback.print_exc()
        self.manager.drop_table('migrate-postgresql', 't2')
        print "droped table t2"
        self.manager.drop_db('migrate-postgresql')
        self.manager.close('migrate-postgresql')

    def test_reconnect(self):
        """test reconnect to database"""
#       postgresql
        self.manager.connect(self.p_url)
        self.manager.reconnect('test-postgresql')
        self.manager.close('test-postgresql')

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

