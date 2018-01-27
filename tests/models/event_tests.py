import unittest
from datetime import datetime, timezone
from app.models.persistence.event import EventDataModel
from freezegun import freeze_time


class EventTests(unittest.TestCase):
    def setUp(self):
        self.event_id = 'test_id'
        self.hares = ['hare1', 'hare2']
        self.name = 'test event'
        self.description = 'An event to test dynamodb persistence'
        self.kennels = ['kennel1']
        self.type = 'basic'
        self.start_time = datetime.now(tz=timezone.utc)
        self.end_time = self.start_time
        self.start_location = 'location1'
        self.trails = ['trail1']
        self.event = EventDataModel(self.event_id, hares=self.hares, name=self.name, description=self.description,
                                    kennels=self.kennels, type=self.type, start_time=self.start_time,
                                    end_time=self.end_time, start_location=self.start_location, trails=self.trails)
        self.event.save()

    @classmethod
    def setUpClass(cls):
        EventDataModel.Meta.host = 'http://localhost:8000'
        EventDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    @classmethod
    def tearDownClass(cls):
        if EventDataModel.exists():
            EventDataModel.delete_table()

    def tearDown(self):
        if self.event.exists():
            self.event.delete()

    def test_create_and_retrieve(self):
        self.assertTrue(self.event.exists())
        retrieved_obj = EventDataModel.get(self.event_id)
        self.assertEqual(retrieved_obj, self.event)

    def test_update(self):
        new_type = 'different type'
        self.event.update(actions=[EventDataModel.type.set(new_type)])
        self.event.refresh()
        retrieved_obj = EventDataModel.get(self.event_id)
        self.assertEqual(retrieved_obj, self.event)
        self.assertTrue(retrieved_obj.type, new_type)

    def test_delete(self):
        self.assertTrue(self.event.exists())
        self.event.delete()
        with self.assertRaises(EventDataModel.DoesNotExist):
            EventDataModel.get(self.event_id)

    def test_set_host(self):
        new_host = 'http://www.notreal.org:8000'
        self.event.host(new_host)
        self.assertEqual(new_host, self.event.host())
        self.assertEqual(EventDataModel.Meta.host, new_host)

    def test_get_host(self):
        self.assertEqual('http://localhost:8000', self.event.host())

    def test_timestamps(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            event = EventDataModel(self.event_id, hares=self.hares, name=self.name, description=self.description,
                                   kennels=self.kennels, type=self.type, start_time=self.start_time,
                                   end_time=self.end_time, start_location=self.start_location, trails=self.trails)
            event.save()
            self.assertEqual(event.modified_at, time)
            self.assertEqual(event.created_at, time)
