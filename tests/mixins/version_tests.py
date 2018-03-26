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
        model.add_update_action('field1', 'set', 'different')
        model.update()
        self.assertEqual(model.version, 1)

    def test_multiple_updates(self):
        model = VersionTestModel('test', field1='test_1', field2='test_2')
        model.save()
        self.assertEqual(model.version, 0)
        model.add_update_action('field1', 'set', 'different')
        model.update()
        self.assertEqual(model.version, 1)
        model.add_update_action('field1', 'set', 'different2')
        model.update()
        self.assertEqual(model.version, 2)
        model.add_update_action('field1', 'set', 'different3')
        model.update()
        self.assertEqual(model.version, 3)

    def test_non_changing_update(self):
        model = VersionTestModel('test', field1='test_1', field2='test_2')
        model.save()
        self.assertEqual(model.version, 0)
        model.add_update_action('field1', 'set', 'different')
        model.update()
        self.assertEqual(model.version, 1)
        model.add_update_action('field1', 'set', 'different')
        model.update()
        self.assertEqual(model.version, 2)

    def test_attributes(self):
        model = VersionTestModel('test', field1='test_1', field2='test_2')
        model.save()
        result = VersionTestModel.get('test')
        attributes = result.attributes()
        for key in model.__meta_attributes__:
            self.assertNotIn(key, attributes.keys())

    def test_update_create(self):
        model = VersionTestModel('test')
        model.add_update_action('field1', 'set', 'test_1')
        model.add_update_action('field2', 'set', 'test_2')
        model.update()
        self.assertEqual(model.version, 0)
        retrieved = VersionTestModel.get('test')
        self.assertEqual(retrieved.version, 0)

    @classmethod
    def tearDownClass(cls):
        if VersionTestModel.exists():
            VersionTestModel.delete_table()
