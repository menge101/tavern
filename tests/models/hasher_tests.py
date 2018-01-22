import unittest
from datetime import datetime, timezone
from app.models.persistence.hasher import HasherDataModel
from freezegun import freeze_time


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
    def tearDownClass(cls):
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

    def test_timestamps(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name, user=self.user)
            hasher.save()
        self.assertEqual(hasher.modified_at, time)
        self.assertEqual(hasher.created_at, time)

    def test_timestamps_on_update(self):
        new_kennel = 'p2h2'
        start_time = datetime.now(timezone.utc)
        with freeze_time(start_time):
            hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name, user=self.user)
            hasher.save()
        mid_time = datetime.now(timezone.utc)
        with freeze_time(mid_time):
            hasher.update(actions=[HasherDataModel.mother_kennel.set(new_kennel)])
        self.assertEqual(hasher.modified_at, mid_time)
        self.assertEqual(hasher.created_at, start_time)
        self.assertEqual(hasher.mother_kennel, new_kennel)
