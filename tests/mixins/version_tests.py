import unittest
from .version_test_model import VersionTestModel


class VersionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        VersionTestModel.Meta.host = 'http://localhost:8000'
        if VersionTestModel.exists():
            VersionTestModel.delete_table()
        VersionTestModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def test_create_with_null_field(self):
        model = VersionTestModel('test', field1='test_1')
        model.save()
        actual = VersionTestModel.get('test')
        self.assertEqual(actual.version, 0)

    def test_create(self):
        model = VersionTestModel('test2', field1='test_1', field2='test_2')
        model.save()
        actual = VersionTestModel.get('test2')
        self.assertEqual(actual.version, 0)

    def test_update(self):
        model = VersionTestModel('test', field1='test_1', field2='test_2')
        model.save()
        self.assertEqual(model.version, 0)
        model.update(actions=[VersionTestModel.field1.set('different')])
        self.assertEqual(model.version, 1)

    def test_multiple_updates(self):
        model = VersionTestModel('test', field1='test_1', field2='test_2')
        model.save()
        self.assertEqual(model.version, 0)
        model.update(actions=[VersionTestModel.field1.set('different')])
        self.assertEqual(model.version, 1)
        model.update(actions=[VersionTestModel.field1.set('different2')])
        self.assertEqual(model.version, 2)
        model.update(actions=[VersionTestModel.field1.set('different3')])
        self.assertEqual(model.version, 3)

    def test_non_changing_update(self):
        model = VersionTestModel('test', field1='test_1', field2='test_2')
        model.save()
        self.assertEqual(model.version, 0)
        model.update(actions=[VersionTestModel.field1.set('different')])
        self.assertEqual(model.version, 1)
        model.update(actions=[VersionTestModel.field1.set('different')])
        self.assertEqual(model.version, 2)

    @classmethod
    def tearDownClass(cls):
        if VersionTestModel.exists():
            VersionTestModel.delete_table()
