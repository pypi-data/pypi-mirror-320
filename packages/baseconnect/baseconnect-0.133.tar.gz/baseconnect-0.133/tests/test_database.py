# tests/test_database.py
import unittest
from baseconnect import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database(server='your_server', database='your_db')

    def test_connection(self):
        self.db.connect()
        self.assertIsNotNone(self.db.conn)
        self.db.close()


if __name__ == '__main__':
    unittest.main()
