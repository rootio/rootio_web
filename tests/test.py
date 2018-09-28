import os
import rootio
import unittest
import tempfile

class RootioTestCase(unittest.TestCase):

    def setUp(self):
        rootio.app.testing = True
        self.app = rootio.app

    def tearDown(self):
        os.close(self.db)

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

if __name__ == '__main__':
    unittest.main()
