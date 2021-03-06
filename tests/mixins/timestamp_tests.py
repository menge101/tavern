import unittest
from datetime import datetime, timezone
from freezegun import freeze_time


from .timestamp_test_model import TimestampTestModel


class TimestampTests(unittest.TestCase):
    def setUp(self):
        self.model = TimestampTestModel('test', field='test_1')

    @classmethod
    def setUpClass(cls):
        if TimestampTestModel.exists():
            TimestampTestModel.delete_table()
        TimestampTestModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def test_save(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            self.model.save()
            self.assertEqual(self.model.modified_at, time)
            self.assertEqual(self.model.created_at, time)

    def test_update(self):
        start_time = datetime.now(timezone.utc)
        with freeze_time(start_time):
            self.model.save()
        after_save = datetime.now(timezone.utc)
        with freeze_time(after_save):
            self.model.add_update_action('field', 'set', 'test_2')
            self.model.update()
        result = TimestampTestModel.get('test')
        self.assertEqual(result.created_at, start_time)
        self.assertEqual(result.modified_at, after_save)

    def test_attributes(self):
        self.model.save()
        result = TimestampTestModel.get('test')
        attributes = result.attributes()
        for key in self.model.__meta_attributes__:
            self.assertNotIn(key, attributes.keys())

    def tearDown(self):
        self.model.delete()

    @classmethod
    def tearDownClass(cls):
        if TimestampTestModel.exists():
            TimestampTestModel.delete_table()
