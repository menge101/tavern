import geohash
import unittest
from app.models.logic.location import LocationLogicModel
from app.models.persistence.location import LocationDataModel
from tests.models import logic


class LocationLogicTests(unittest.TestCase):
    def setUp(self):
        self.location_id = 'test_location_id'
        self.name = "D's 6-pax & Dogz"
        self.searchable_name = LocationDataModel.searchable_value(self.name)
        self.address1 = '1118 S Braddock Ave'
        self.address2 = 'First floor'
        self.city = 'Swissvale'
        self.state = 'PA'
        self.postal = '15218'
        self.country = 'usa'
        self.latitude = 40.4320562
        self.longitude = -79.8959572
        self.geohash = geohash.encode(self.latitude, self.longitude)
        logic.clean_create_tables([LocationDataModel])

    def test_init_all_data(self):
        loc = LocationLogicModel(self.name, location_id=self.location_id, searchable_name=self.searchable_name,
                                 address1=self.address1, address2=self.address2, city=self.city,
                                 state_province_region=self.state, country=self.country, postal_code=self.postal,
                                 longitude=self.longitude, latitude=self.latitude, geohash=self.geohash)
        self.assertEqual(loc.location_id, self.location_id)
        self.assertEqual(loc.name, self.name)
        self.assertEqual(loc.geohash, self.geohash)
        self.assertEqual(loc.searchable_name, self.searchable_name)
        self.assertEqual(loc.address1, self.address1)
        self.assertEqual(loc.address2, self.address2)
        self.assertEqual(loc.city, self.city)
        self.assertEqual(loc.state_province_region, self.state)
        self.assertEqual(loc.country, self.country)
        self.assertEqual(loc.postal_code, self.postal)
        self.assertEqual(loc.longitude, self.longitude)
        self.assertEqual(loc.latitude, self.latitude)

    def test_no_geohash(self):
        loc = LocationLogicModel(self.name, location_id=self.location_id, searchable_name=self.searchable_name,
                                 address1=self.address1, address2=self.address2, city=self.city,
                                 state_province_region=self.state, country=self.country, postal_code=self.postal,
                                 longitude=self.longitude, latitude=self.latitude)
        self.assertEqual(loc.location_id, self.location_id)
        self.assertEqual(loc.name, self.name)
        self.assertEqual(loc.geohash, self.geohash)
        self.assertEqual(loc.searchable_name, self.searchable_name)
        self.assertEqual(loc.address1, self.address1)
        self.assertEqual(loc.address2, self.address2)
        self.assertEqual(loc.city, self.city)
        self.assertEqual(loc.state_province_region, self.state)
        self.assertEqual(loc.country, self.country)
        self.assertEqual(loc.postal_code, self.postal)
        self.assertEqual(loc.longitude, self.longitude)
        self.assertEqual(loc.latitude, self.latitude)

    def test_no_latlng(self):
        loc = LocationLogicModel(self.name, location_id=self.location_id, searchable_name=self.searchable_name,
                                 address1=self.address1, address2=self.address2, city=self.city,
                                 state_province_region=self.state, country=self.country, postal_code=self.postal,
                                 geohash=self.geohash)
        self.assertEqual(loc.location_id, self.location_id)
        self.assertEqual(loc.name, self.name)
        self.assertEqual(loc.geohash, self.geohash)
        self.assertEqual(loc.searchable_name, self.searchable_name)
        self.assertEqual(loc.address1, self.address1)
        self.assertEqual(loc.address2, self.address2)
        self.assertEqual(loc.city, self.city)
        self.assertEqual(loc.state_province_region, self.state)
        self.assertEqual(loc.country, self.country)
        self.assertEqual(loc.postal_code, self.postal)
        self.assertAlmostEqual(loc.longitude, self.longitude)
        self.assertAlmostEqual(loc.latitude, self.latitude, places=6)

    def test_only_address(self):
        with self.assertRaises(ValueError):
            LocationLogicModel(self.name, location_id=self.location_id, searchable_name=self.searchable_name,
                               address1=self.address1, address2=self.address2, city=self.city,
                               state_province_region=self.state, country=self.country, postal_code=self.postal)

