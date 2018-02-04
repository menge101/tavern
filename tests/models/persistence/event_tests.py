import unittest
from datetime import datetime, timezone
from app.models.persistence.event import EventDataModel, HareEventDataModel, KennelEventDataModel
from app.models.persistence.hasher import HasherReferenceModel
from app.models.persistence.kennel import KennelReferenceModel
from freezegun import freeze_time


class EventTests(unittest.TestCase):
    def setUp(self):
        self.event_id = 'test_id'
        self.hares = [HasherReferenceModel(hasher_id='hare_1', hash_name='Harry One'),
                      HasherReferenceModel(hasher_id='hare_2', hash_name='Harry Two')]
        self.name = 'test event'
        self.description = 'An event to test dynamodb persistence'
        self.kennels = [KennelReferenceModel(kennel_id='kennel_1', name='One HHH', acronym='1H3')]
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
        retrieved_obj = EventDataModel.get(self.event_id, self.start_time)
        self.event.refresh()
        self.assertEqual(retrieved_obj, self.event)

    def test_update(self):
        new_type = 'different type'
        self.event.update(actions=[EventDataModel.type.set(new_type)])
        self.event.refresh()
        retrieved_obj = EventDataModel.get(self.event_id, self.start_time)
        self.assertEqual(retrieved_obj, self.event)
        self.assertTrue(retrieved_obj.type, new_type)

    def test_delete(self):
        self.assertTrue(self.event.exists())
        self.event.delete()
        with self.assertRaises(EventDataModel.DoesNotExist):
            EventDataModel.get(self.event_id, self.start_time)

    def test_timestamps(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            event = EventDataModel(self.event_id, hares=self.hares, name=self.name, description=self.description,
                                   kennels=self.kennels, type=self.type, start_time=self.start_time,
                                   end_time=self.end_time, start_location=self.start_location, trails=self.trails)
            event.save()
            self.assertEqual(event.modified_at, time)
            self.assertEqual(event.created_at, time)

    def test_to_ref(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            event = EventDataModel(self.event_id, hares=self.hares, name=self.name, description=self.description,
                                   kennels=self.kennels, type=self.type, start_time=self.start_time,
                                   end_time=self.end_time, start_location=self.start_location, trails=self.trails)
            event.save()
        ref = event.to_ref()
        self.assertEqual(ref.event_id, self.event_id)
        self.assertListEqual(ref.hares, self.hares)
        self.assertEqual(ref.description, self.description)
        self.assertListEqual(ref.kennels, self.kennels)
        self.assertEqual(ref.start_time, self.start_time)
        self.assertEqual(ref.start_location, self.start_location)


class EventReferenceModelTests(unittest.TestCase):
    def setUp(self):
        self.event_id = 'test_id'
        self.hares = [HasherReferenceModel(hasher_id='hare_1', hash_name='Harry One'),
                      HasherReferenceModel(hasher_id='hare_2', hash_name='Harry Two')]
        self.name = 'test event'
        self.description = 'An event to test dynamodb persistence'
        self.kennels = [KennelReferenceModel(kennel_id='kennel_1', name='One HHH', acronym='1H3')]
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
        EventDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    @classmethod
    def tearDownClass(cls):
        if EventDataModel.exists():
            EventDataModel.delete_table()

    def tearDown(self):
        if self.event.exists():
            self.event.delete()

    def test_create_event_ref(self):
        ref = self.event.to_ref()
        self.assertTrue(hasattr(ref, 'event_id'))
        self.assertTrue(hasattr(ref, 'hares'))
        self.assertTrue(hasattr(ref, 'name'))
        self.assertTrue(hasattr(ref, 'description'))
        self.assertTrue(hasattr(ref, 'kennels'))
        self.assertTrue(hasattr(ref, 'start_time'))
        self.assertTrue(hasattr(ref, 'start_location'))

    def test_is_ref_of(self):
        ref = self.event.to_ref()
        self.assertTrue(ref.is_ref_of(self.event))


class HareEventTests(unittest.TestCase):
    def setUp(self):
        self.event_id = 'test_id'
        self.hares = [HasherReferenceModel(hasher_id='hare_1', hash_name='Harry One'),
                      HasherReferenceModel(hasher_id='hare_2', hash_name='Harry Two')]
        self.name = 'test event'
        self.description = 'An event to test dynamodb persistence'
        self.kennels = [KennelReferenceModel(kennel_id='kennel_1', name='One HHH', acronym='1H3')]
        self.type = 'basic'
        self.start_time = datetime.now(tz=timezone.utc)
        self.end_time = self.start_time
        self.start_location = 'location1'
        self.trails = ['trail1']
        self.event = EventDataModel(self.event_id, hares=self.hares, name=self.name, description=self.description,
                                    kennels=self.kennels, type=self.type, start_time=self.start_time,
                                    end_time=self.end_time, start_location=self.start_location, trails=self.trails)
        self.event.save()
        self.ref = self.event.to_ref()
        self.hare_event = HareEventDataModel(self.hares[0].hasher_id, start_time=self.start_time,
                                             event_id=self.event_id, event_ref=self.ref)
        self.hare_event.save()

    @classmethod
    def setUpClass(cls):
        EventDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        HareEventDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    @classmethod
    def tearDownClass(cls):
        if EventDataModel.exists():
            EventDataModel.delete_table()
        if HareEventDataModel.exists():
            HareEventDataModel.delete_table()

    def tearDown(self):
        if self.hare_event.exists():
            self.hare_event.delete()

    def test_create_and_retrieve(self):
        self.assertTrue(self.hare_event.exists())
        retrieved_obj = HareEventDataModel.get(self.hares[0].hasher_id, self.hare_event.start_time)
        self.hare_event.refresh()
        self.assertEqual(retrieved_obj, self.hare_event)

    def test_update(self):
        self.hare_event.update(actions=[HareEventDataModel.event_id.set('changed')])
        self.hare_event.refresh()
        retrieved_obj = HareEventDataModel.get(self.hares[0].hasher_id, self.hare_event.start_time)
        self.assertEqual(retrieved_obj, self.hare_event)
        self.assertTrue(retrieved_obj.event_id, 'changed')

    def test_delete(self):
        self.assertTrue(self.hare_event.exists())
        self.hare_event.delete()
        with self.assertRaises(HareEventDataModel.DoesNotExist):
            HareEventDataModel.get(self.hares[0].hasher_id, self.hare_event.start_time)


class KennelEventTests(unittest.TestCase):
    def setUp(self):
        self.event_id = 'test_id'
        self.hares = [HasherReferenceModel(hasher_id='hare_1', hash_name='Harry One'),
                      HasherReferenceModel(hasher_id='hare_2', hash_name='Harry Two')]
        self.name = 'test event'
        self.description = 'An event to test dynamodb persistence'
        self.kennels = [KennelReferenceModel(kennel_id='kennel_1', name='One HHH', acronym='1H3')]
        self.type = 'basic'
        self.start_time = datetime.now(tz=timezone.utc)
        self.end_time = self.start_time
        self.start_location = 'location1'
        self.trails = ['trail1']
        self.event = EventDataModel(self.event_id, hares=self.hares, name=self.name, description=self.description,
                                    kennels=self.kennels, type=self.type, start_time=self.start_time,
                                    end_time=self.end_time, start_location=self.start_location, trails=self.trails)
        self.event.save()
        self.ref = self.event.to_ref()
        self.kennel_event = KennelEventDataModel(self.kennels[0].kennel_id, start_time=self.start_time,
                                                 event_id=self.event_id, event_ref=self.ref)
        self.kennel_event.save()

    @classmethod
    def setUpClass(cls):
        EventDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        KennelEventDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    @classmethod
    def tearDownClass(cls):
        if EventDataModel.exists():
            EventDataModel.delete_table()
        if KennelEventDataModel.exists():
            KennelEventDataModel.delete_table()

    def tearDown(self):
        if self.kennel_event.exists():
            self.kennel_event.delete()

    def test_create_and_retrieve(self):
        self.assertTrue(self.kennel_event.exists())
        retrieved_obj = KennelEventDataModel.get(self.kennels[0].kennel_id, self.kennel_event.start_time)
        self.kennel_event.refresh()
        self.assertEqual(retrieved_obj, self.kennel_event)

    def test_update(self):
        self.kennel_event.update(actions=[KennelEventDataModel.event_id.set('changed')])
        self.kennel_event.refresh()
        retrieved_obj = KennelEventDataModel.get(self.kennels[0].kennel_id, self.kennel_event.start_time)
        self.assertEqual(retrieved_obj, self.kennel_event)
        self.assertTrue(retrieved_obj.event_id, 'changed')

    def test_delete(self):
        self.assertTrue(self.kennel_event.exists())
        self.kennel_event.delete()
        with self.assertRaises(KennelEventDataModel.DoesNotExist):
            KennelEventDataModel.get(self.hares[0].hasher_id, self.kennel_event.start_time)
