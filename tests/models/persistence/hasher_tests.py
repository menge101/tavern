import unittest
from datetime import datetime, timezone
from app.models.persistence import AlreadyExists
from app.models.persistence.hasher import HasherDataModel
from freezegun import freeze_time


class HasherTests(unittest.TestCase):
    def setUp(self):
        self.hasher_id = 'test_id'
        self.name = 'test_hasher'
        self.kennel = 'test_kennel'
        self.user = 'test_user'
        if HasherDataModel.exists():
            HasherDataModel.delete_table()
        HasherDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def tearDown(self):
        if HasherDataModel.exists():
            HasherDataModel.delete_table()

    def test_nullable_fields(self):
        hasher = HasherDataModel(self.hasher_id, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), mother_kennel=self.kennel)
        hasher.save()
        self.assertIsNone(hasher.contact_info)
        self.assertIsNone(hasher.real_name)
        self.assertIsNone(hasher.user)

    def test_id_required(self):
        with self.assertRaises(ValueError):
            HasherDataModel(hash_name=self.name, lower_hash_name=self.name.lower(),
                            mother_kennel=self.kennel).save()

    def test_name_required(self):
        with self.assertRaises(ValueError):
            HasherDataModel(self.hasher_id, lower_hash_name=self.name.lower(), mother_kennel=self.kennel).save()

    def test_kennel_required(self):
        with self.assertRaises(ValueError):
            HasherDataModel(self.hasher_id, lower_hash_name=self.name.lower(), hash_name=self.name).save()

    def test_timestamps(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                                     lower_hash_name=self.name.lower(), user=self.user)
            hasher.save()
        self.assertEqual(hasher.modified_at, time)
        self.assertEqual(hasher.created_at, time)

    def test_timestamps_on_update(self):
        new_kennel = 'p2h2'
        start_time = datetime.now(timezone.utc)
        with freeze_time(start_time):
            hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                                     lower_hash_name=self.name.lower(), user=self.user)
            hasher.save()
        mid_time = datetime.now(timezone.utc)
        with freeze_time(mid_time):
            hasher.update(actions=[HasherDataModel.mother_kennel.set(new_kennel)])
        self.assertEqual(hasher.modified_at, mid_time)
        self.assertEqual(hasher.created_at, start_time)
        self.assertEqual(hasher.mother_kennel, new_kennel)

    def test_record_exists(self):
        hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), user=self.user)
        hasher.save()
        self.assertTrue(HasherDataModel.record_exists(hasher))

    def test_record_does_not_exist(self):
        hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), user=self.user)
        self.assertFalse(HasherDataModel.record_exists(hasher))

    def test_matching_records_does_not_exist(self):
        hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), user=self.user)
        self.assertListEqual(HasherDataModel.matching_records(hasher), list())

    def test_matching_record_filtering_self(self):
        hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), user=self.user)
        hasher.save()
        self.assertListEqual(HasherDataModel.matching_records(hasher), list())

    def test_matching_record_not_filtering_self(self):
        hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), user=self.user)
        hasher.save()
        self.assertListEqual(HasherDataModel.matching_records(hasher, False), [hasher])

    def test_matching_record_with_different_users(self):
        HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                        lower_hash_name=self.name.lower(), user=self.user).save()
        hasher = HasherDataModel(self.hasher_id, mother_kennel=self.kennel, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), user='different_user')
        self.assertListEqual(HasherDataModel.matching_records(hasher), list())

    def test_matching_records_multiple_close_matches(self):
        HasherDataModel('hasher1', mother_kennel=self.kennel, hash_name=self.name,
                        lower_hash_name=self.name.lower(), user=self.user).save()
        two = HasherDataModel('hasher2', mother_kennel=self.kennel, hash_name=self.name,
                              lower_hash_name=self.name.lower(), user='user2')
        two.save()
        HasherDataModel('hasher3', mother_kennel=self.kennel, hash_name=self.name,
                        lower_hash_name=self.name.lower(), user='user3').save()
        hasher = HasherDataModel('hasher4', mother_kennel=self.kennel, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), user='user2')
        x = HasherDataModel.matching_records(hasher)
        self.assertListEqual(x, [two])

    def test_save_with_existing_record(self):
        HasherDataModel('hasher1', mother_kennel=self.kennel, hash_name=self.name,
                        lower_hash_name=self.name.lower()).save()
        with self.assertRaises(AlreadyExists):
            HasherDataModel('hasher2', mother_kennel=self.kennel, hash_name=self.name,
                            lower_hash_name=self.name.lower()).save()

    def test_save_with_no_user_existing_record(self):
        start = HasherDataModel('hasher1', mother_kennel=self.kennel, hash_name=self.name,
                                lower_hash_name=self.name.lower())
        start.save()
        hasher = HasherDataModel('hasher1', mother_kennel=self.kennel, hash_name=self.name,
                                 lower_hash_name=self.name.lower(), user='user1')
        hasher.save()
        self.assertTrue(HasherDataModel.record_exists(start))
        self.assertTrue(HasherDataModel.record_exists(hasher))

    def test_save_same_record_twice(self):
        start = HasherDataModel('hasher1', mother_kennel=self.kennel, hash_name=self.name,
                                lower_hash_name=self.name.lower())
        start.save()
        start.save()
        self.assertTrue(HasherDataModel.record_exists(start))
