import unittest

from app.models.persistence.kennel import KennelDataModel


class KennelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        KennelDataModel.Meta.host = 'http://localhost:8000'
        KennelDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        
    def setUp(self):
        self.kennel_id = 'test_id'
        self.name = 'test_kennel'
        self.acronym = 'tkh3'
        self.region = ['1.1', '1.2', '2.2', '2.1']
        self.events = ['event1', 'event2', 'event3']
        self.members = ['hasher1', 'hasher2', 'hasher3']
        self.officers = {'grand matress': 'gm_hasher', 'religous advisor': 'ra_hasher', 'hash cash': 'hash_cash_hasher'}

    @classmethod
    def TearDownClass(cls):
        if KennelDataModel.exists():
            KennelDataModel.delete_table()

    def test_nullable_fields(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        self.assertIsNone(kennel.region)
        self.assertIsNone(kennel.events)
        self.assertIsNone(kennel.members)
        self.assertIsNone(kennel.officers)

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
