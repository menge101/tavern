import unittest
from app.models.logic.kennel import KennelLogicModel
from app.models.persistence.kennel import KennelDataModel


class KennelLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        KennelDataModel.Meta.host = 'http://localhost:8000'
        KennelDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def setUp(self):
        self.kennel_id = 'test_id'
        self.name = 'test_kennel'
        self.acronym = 'tkh3'

    def test_init_from_lookup(self):
        KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym).save()
        x = KennelLogicModel.lookup_by_id(self.kennel_id)
        self.assertEqual(self.kennel_id, x.kennel_id)
        self.assertEqual(self.name, x.name)
        self.assertEqual(self.acronym, x.acronym)

    def test_create(self):
        actual = KennelLogicModel.create(self.name, self.acronym)
        expected = KennelLogicModel.lookup_by_id(actual.kennel_id)
        self.assertEqual(actual, expected)
        self.assertEqual(actual.name, self.name)
        self.assertEqual(actual.acronym, self.acronym)

    @classmethod
    def tearDownClass(cls):
        if KennelDataModel.exists():
            KennelDataModel.delete_table()
