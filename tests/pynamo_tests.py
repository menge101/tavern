import unittest
from datetime import datetime
import pynamodb.exceptions
from .pynamo_test_model import PynamoTestModel


class PynamoTests(unittest.TestCase):
    def setUp(self):
        self.test_id = 'test_id'
        self.list = ['item1', 'item2']
        self.description = 'A test of dynamodb persistence'
        self.start_time = datetime.now()
        self.end_time = self.start_time
        PynamoTestModel.Meta.host = 'http://localhost:8000'
        if PynamoTestModel.exists():
            PynamoTestModel.delete_table()

    def tearDown(self):
        if PynamoTestModel.exists():
            PynamoTestModel.delete_table()

    def test_create_with_no_table_existing(self):
        with self.assertRaises(pynamodb.exceptions.TableDoesNotExist):
            PynamoTestModel(self.test_id, list=self.list, description=self.description, start_time=self.start_time,
                            end_time=self.end_time)

    def test_table_create(self):
        self.assertFalse(PynamoTestModel.exists())
        PynamoTestModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        self.assertTrue(PynamoTestModel.exists())

    def test_table_delete(self):
        PynamoTestModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        self.assertTrue(PynamoTestModel.exists())
        PynamoTestModel.delete_table()
        self.assertFalse(PynamoTestModel.exists())
