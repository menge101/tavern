import unittest
from datetime import datetime, timezone
from freezegun import freeze_time
from app.models.persistence import AlreadyExists
from app.models.persistence.event import EventReferenceModel
from app.models.persistence.hasher import HasherReferenceModel
from app.models.persistence.kennel import KennelReferenceModel
from app.models.persistence.location import EventLocationDataModel, LocationDataModel, LocationReferenceModel


class LocationTests(unittest.TestCase):
    def setUp(self):
        self.location_id = 'testid'
        self.geohash = 'AAAA1111'
        self.name = 'Test Location'
        self.searchable_name = LocationDataModel.searchable_value(self.name)
        self.address1 = '123 Fake st.'
        self.address2 = 'c/o Fake Person'
        self.city = 'Fakesville'
        self.state_province_region = 'FK'
        self.postal_code = '12345-6789'
        self.country = 'united states of america'
        self.latitude = 123.987654
        self.longitude = 85.12345
        self.location = LocationDataModel(self.location_id, name=self.name, searchable_name=self.searchable_name,
                                          address1=self.address1, address2=self.address2, city=self.city,
                                          state_province_region=self.state_province_region,
                                          postal_code=self.postal_code, country=self.country, longitude=self.longitude,
                                          latitude=self.latitude, geohash=self.geohash)
        self.location.save()

    @classmethod
    def setUpClass(cls):
        LocationDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    @classmethod
    def tearDownClass(cls):
        if LocationDataModel.exists():
            LocationDataModel.delete_table()

    def tearDown(self):
        if self.location.exists():
            self.location.delete()

    def test_create_retrieve(self):
        self.assertTrue(self.location.exists())
        retrieved_obj = LocationDataModel.get(self.location_id)
        self.location.refresh()
        self.assertEqual(retrieved_obj, self.location)

    def test_searchable_name_prefix_suffix(self):
        self.assertEqual(self.location.searchable_name_prefix, 'tes')
        self.assertEqual(self.location.searchable_name_suffix, 'tlocation')

    def test_update(self):
        new_lat = 0.0
        self.location.update(actions=[LocationDataModel.latitude.set(new_lat)])
        self.location.refresh()
        retrieved_obj = LocationDataModel.get(self.location_id)
        self.assertEqual(retrieved_obj, self.location)
        self.assertEqual(retrieved_obj.latitude, new_lat)

    def test_delete(self):
        self.assertTrue(self.location.exists())
        self.location.delete()
        with self.assertRaises(LocationDataModel.DoesNotExist):
            LocationDataModel.get(self.location_id)

    def test_timestamps(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            loc = LocationDataModel(self.location_id, searchable_name=self.searchable_name, name=self.name,
                                    address1=self.address1, address2=self.address2, city=self.city,
                                    state_province_region=self.state_province_region,
                                    postal_code=self.postal_code, country=self.country, longitude=self.longitude,
                                    latitude=self.latitude, geohash='BBBB2222')
            loc.save()
            self.assertEqual(loc.modified_at, time)
            self.assertEqual(loc.created_at, time)

    def test_to_ref(self):
        ref = self.location.to_ref()
        self.assertEqual(ref.geohash, self.geohash)
        self.assertEqual(ref.name, self.name)
        self.assertEqual(ref.address1, self.address1)
        self.assertEqual(ref.address2, self.address2)
        self.assertEqual(ref.city, self.city)
        self.assertEqual(ref.state_province_region, self.state_province_region)
        self.assertEqual(ref.postal_code, self.postal_code)
        self.assertEqual(ref.latitude, self.latitude)
        self.assertEqual(ref.longitude, self.longitude)
        self.assertEqual(ref.country, self.country)

    def test_is_ref_of(self):
        ref = LocationReferenceModel(geohash=self.geohash, name=self.name, address1=self.address1,
                                     address2=self.address2, city=self.city,
                                     state_province_region=self.state_province_region, postal_code=self.postal_code,
                                     latitude=self.latitude, longitude=self.longitude)
        self.assertTrue(ref.is_ref_of(self.location))

    def test_create_duplicate_location(self):
        dupe = LocationDataModel('dupe_test', searchable_name=self.searchable_name, name=self.name,
                                 address1=self.address1, address2=self.address2, city=self.city,
                                 state_province_region=self.state_province_region,
                                 postal_code=self.postal_code, country=self.country, longitude=self.longitude,
                                 latitude=self.latitude, geohash=self.geohash)
        with self.assertRaises(AlreadyExists):
            dupe.save()

    def test_create_same_name_different_place(self):
        also = LocationDataModel('also_test', searchable_name=self.searchable_name, name=self.name,
                                 address1=self.address1, address2=self.address2, city=self.city,
                                 state_province_region=self.state_province_region,
                                 postal_code=self.postal_code, country=self.country, longitude=self.longitude,
                                 latitude=self.latitude, geohash='AAAABBBB')
        also.save()
        results = LocationDataModel.location_name_index.count(self.searchable_name)
        self.assertEqual(results, 2)


class EventLocationTests(unittest.TestCase):
    def setUp(self):
        self.geohash = 'aaaa1111'
        self.name = 'Test Location'
        self.searchable_name = LocationDataModel.searchable_value(self.name)
        self.address1 = '123 Fake st.'
        self.address2 = 'c/o Fake Person'
        self.city = 'Fakesville'
        self.state_province_region = 'FK'
        self.postal_code = '12345-6789'
        self.country = 'US'
        self.latitude = 123.987654
        self.longitude = 85.12345
        self.location_ref = LocationReferenceModel(geohash=self.geohash, name=self.name, address1=self.address1,
                                                   address2=self.address2, city=self.city,
                                                   state_province_region=self.state_province_region,
                                                   postal_code=self.postal_code, country=self.country,
                                                   longitude=self.longitude, latitude=self.latitude)
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
        self.event_ref = EventReferenceModel(event_id=self.event_id, hares=self.hares, name=self.name,
                                             description=self.description, kennels=self.kennels,
                                             start_location=self.start_location, start_time=self.start_time)
        self.event_loc = EventLocationDataModel(self.geohash, self.start_time, location_ref=self.location_ref,
                                                event_ref=self.event_ref)
        self.event_loc.save()

    @classmethod
    def setUpClass(cls):
        EventLocationDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    @classmethod
    def tearDownClass(cls):
        if EventLocationDataModel.exists():
            EventLocationDataModel.delete_table()

    def tearDown(self):
        if self.event_loc.exists():
            self.event_loc.delete()

    def test_create(self):
        obj = EventLocationDataModel.get(self.geohash, self.start_time)
        self.assertEqual(obj.geohash, self.geohash)
        self.assertEqual(obj.start_time, self.start_time)
        self.assertEqual(obj.location_ref, self.location_ref)
        self.event_ref.hares = [obj.attribute_values for obj in self.event_ref.hares]
        self.event_ref.kennels = [obj.attribute_values for obj in self.event_ref.kennels]
        self.assertEqual(obj.event_ref, self.event_ref)

    def test_delete(self):
        self.assertTrue(self.event_loc.exists())
        self.event_loc.delete()
        with self.assertRaises(EventLocationDataModel.DoesNotExist):
            self.event_loc.refresh()
