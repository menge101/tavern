import unittest
from app.models.logic.hasher import HasherLogicModel
from app.models.logic.kennel import KennelLogicModel
from app.models.persistence import AlreadyExists
from app.models.persistence.hasher import HasherDataModel
from app.models.persistence.kennel import KennelDataModel


class HasherLogicTests(unittest.TestCase):
    def setUp(self):
        if KennelDataModel.exists():
            KennelDataModel.delete_table()
        KennelDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        self.hasher_id = 'test_id'
        self.hash_name = 'Testy Cream'
        self.mother_kennel = KennelLogicModel.create('Test Kennel 1', 'TK1H3')
        if HasherDataModel.exists():
            HasherDataModel.delete_table()
        HasherDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def test_init_from_lookup(self):
        HasherDataModel(self.hasher_id, hash_name=self.hash_name, lower_hash_name=self.hash_name.lower(),
                        mother_kennel=HasherLogicModel.map_mother_kennel(self.mother_kennel),
                        mother_kennel_name_lower=self.mother_kennel.name.lower()).save()
        actual = HasherLogicModel.lookup_by_id(self.hasher_id)
        self.assertEqual(self.hasher_id, actual.hasher_id)
        self.assertEqual(self.hash_name, actual.hash_name)
        self.assertEqual(self.mother_kennel.kennel_id, actual.mother_kennel.kennel_id)
        self.assertEqual(self.mother_kennel.name, actual.mother_kennel.name)
        self.assertEqual(self.mother_kennel.acronym, actual.mother_kennel.acronym)

    def test_lookup_hasher_doesnt_exist(self):
        with self.assertRaises(HasherDataModel.DoesNotExist):
            HasherLogicModel.lookup_by_id(self.hasher_id)

    def test_create(self):
        actual = HasherLogicModel.create(self.hash_name, self.mother_kennel)
        expected = HasherLogicModel.lookup_by_id(actual.hasher_id)
        self.assertEqual(actual, expected)
        self.assertEqual(actual.hash_name, self.hash_name)
        self.assertEqual(self.mother_kennel.kennel_id, actual.mother_kennel.kennel_id)
        self.assertEqual(self.mother_kennel.name, actual.mother_kennel.name)
        self.assertEqual(self.mother_kennel.acronym, actual.mother_kennel.acronym)

    def test_redundant_create(self):
        HasherLogicModel.create(self.hash_name, self.mother_kennel)
        with self.assertRaises(AlreadyExists):
            HasherLogicModel.create(self.hash_name, self.mother_kennel)

    def tearDown(self):
        if HasherDataModel.exists():
            HasherDataModel.delete_table()
