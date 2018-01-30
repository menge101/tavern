import unittest
from app.models.logic.hasher import HasherLogicModel
from app.models.persistence.hasher import HasherDataModel


class HasherLogicTests(unittest.TestCase):
    def setUp(self):
        self.hasher_id = 'test_id'
        self.hash_name = 'Testy Cream'
        self.mother_kennel = 'test_kennel_id'
        HasherDataModel.Meta.host = 'http://localhost:8000'
        HasherDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def test_init_from_lookup(self):
        HasherDataModel(self.hasher_id, hash_name=self.hash_name, mother_kennel=self.mother_kennel).save()
        x = HasherLogicModel.lookup_by_id(self.hasher_id)
        self.assertEqual(self.hasher_id, x.hasher_id)
        self.assertEqual(self.hash_name, x.hash_name)
        self.assertEqual(self.mother_kennel, x.mother_kennel)

    def test_lookup_hasher_doesnt_exist(self):
        with self.assertRaises(HasherDataModel.DoesNotExist):
            HasherLogicModel.lookup_by_id(self.hasher_id)

    def test_create(self):
        actual = HasherLogicModel.create(self.hash_name, self.mother_kennel)
        expected = HasherLogicModel.lookup_by_id(actual.hasher_id)
        self.assertEqual(actual, expected)
        self.assertEqual(actual.hash_name, self.hash_name)
        self.assertEqual(actual.mother_kennel, self.mother_kennel)

    def test_exists_by_id_for_does_not_exist(self):
        self.assertFalse(HasherLogicModel.exists(self.hasher_id))

    def test_exists_by_name_for_does_not_exist(self):
        self.assertFalse(HasherLogicModel.exists(hash_name=self.hash_name))

    def test_exists_by_id_for_exists(self):
        HasherDataModel(self.hasher_id, hash_name=self.hash_name, mother_kennel=self.mother_kennel).save()
        self.assertTrue(HasherLogicModel.exists(self.hasher_id))

    def test_exists_by_name_for_exists(self):
        HasherDataModel(self.hasher_id, hash_name=self.hash_name, mother_kennel=self.mother_kennel).save()
        self.assertTrue(HasherLogicModel.exists(hash_name=self.hash_name))

    def tearDown(self):
        if HasherDataModel.exists():
            HasherDataModel.delete_table()
