import unittest
from datetime import datetime, timezone
from freezegun import freeze_time
from .multi_mixin_test_model import MultiMixinTestModel


class MultiMixinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        MultiMixinTestModel.Meta.host = 'http://localhost:8000'
        if MultiMixinTestModel.exists():
            MultiMixinTestModel.delete_table()
        MultiMixinTestModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def test_save(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            model = MultiMixinTestModel('test1', field='test_filed')
            model.save()
        actual = MultiMixinTestModel.get('test1')
        self.assertEqual(actual.version, 0)
        self.assertEqual(model.modified_at, time)
        self.assertEqual(model.created_at, time)

    def test_update(self):
        start_time = datetime.now(timezone.utc)
        with freeze_time(start_time):
            model = MultiMixinTestModel('test1', field='test_filed')
            model.save()
        after_save = datetime.now(timezone.utc)
        with freeze_time(after_save):
            model.update(actions=[MultiMixinTestModel.field.set('test_2')])
        result = MultiMixinTestModel.get('test1')
        self.assertEqual(result.created_at, start_time)
        self.assertEqual(result.modified_at, after_save)
        self.assertEqual(result.version, 1)

    @classmethod
    def tearDownClass(cls):
        if MultiMixinTestModel.exists():
            MultiMixinTestModel.delete_table()
