import unittest
from datetime import datetime, timezone
from app.models.persistence.kennel import KennelDataModel
from freezegun import freeze_time


class KennelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        KennelDataModel.Meta.host = 'http://localhost:8000'
        KennelDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def setUp(self):
        self.kennel_id = 'test_id'
        self.name = 'Test_Kennel'
        self.acronym = 'TKH3'
        self.region = ['1.1', '1.2', '2.2', '2.1']
        self.contact = [{'name': 'test person', 'phone': '4445556666', 'email': 'atestemail@test.com'}]
        self.facebook = 'http://www.facebook.com/groups/test_kennel'
        self.webpage = 'http://www.testkennel.com'
        self.founding = {'founder': 'G', 'first trail': '1/1/1930'}
        self.description = 'A test kennel'

    @classmethod
    def tearDownClass(cls):
        if KennelDataModel.exists():
            KennelDataModel.delete_table()

    def test_nullable_fields(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        self.assertIsNone(kennel.region)
        self.assertIsNone(kennel.contact)
        self.assertIsNone(kennel.webpage)
        self.assertIsNone(kennel.facebook)
        self.assertIsNone(kennel.founding)
        self.assertIsNone(kennel.description)

    def test_id_required(self):
        kennel = KennelDataModel(name=self.name, acronym=self.acronym)
        with self.assertRaises(ValueError):
            kennel.save()

    def test_name_required(self):
        kennel = KennelDataModel(self.kennel_id, acronym=self.acronym)
        with self.assertRaises(ValueError):
            kennel.save()

    def test_acronym_required(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name)
        with self.assertRaises(ValueError):
            kennel.save()

    def test_timestamps(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
            kennel.save()
            self.assertEqual(kennel.modified_at, time)
            self.assertEqual(kennel.created_at, time)

    def test_all_fields(self):
        KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym, region=self.region,
                        contact=self.contact, webpage=self.webpage, facebook=self.facebook,
                        founding=self.founding, description=self.description).save()

        kennel = KennelDataModel.get(self.kennel_id)
        self.assertEqual(kennel.region, self.region)
        self.assertEqual(kennel.contact, self.contact)
        self.assertEqual(kennel.webpage, self.webpage)
        self.assertEqual(kennel.facebook, self.facebook)
        self.assertEqual(kennel.founding, self.founding)
        self.assertEqual(kennel.description, self.description)
        self.assertEqual(kennel.lower_name, self.name.lower())
        self.assertEqual(kennel.lower_acronym, self.acronym.lower())
