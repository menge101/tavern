from datetime import datetime, timezone
import unittest
from freezegun import freeze_time

from app.models.persistence.hasher import HasherDataModel


class HasherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        HasherDataModel.Meta.host = 'http://localhost:8000'
        HasherDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def setUp(self):
        self.hasher_id = 'test_id'
        self.name = 'test_hasher'
        self.kennel = 'test_kennel'
        self.user = 'test_user'

    @classmethod
    def TearDownClass(cls):
        if HasherDataModel.exists():
            HasherDataModel.delete_table()

    def test_nullable_fields(self):
        hasher = HasherDataModel(self.hasher_id, hash_name=self.name, mother_kennel=self.kennel)
        hasher.save()
        self.assertIsNone(hasher.contact_info)
        self.assertIsNone(hasher.real_name)
        self.assertIsNone(hasher.user)

    def test_id_required(self):
        with self.assertRaises(ValueError):
            HasherDataModel(hash_name=self.name, mother_kennel=self.kennel).save()

    def test_name_required(self):
        with self.assertRaises(ValueError):
            HasherDataModel(self.hasher_id, mother_kennel=self.kennel).save()

    def test_kennel_required(self):
        with self.assertRaises(ValueError):
            HasherDataModel(self.hasher_id, hash_name=self.name).save()
