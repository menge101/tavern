import unittest
from datetime import datetime, timezone
from app.models.persistence.kennel import KennelMemberDataModel


class KennelMemberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        KennelMemberDataModel.Meta.host = 'http://localhost:8000'
        KennelMemberDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def setUp(self):
        self.kennel_id = 'test_kennel_id'
        self.hasher_id = 'test_hasher_id'
        self.joined = datetime.now(tz=timezone.utc)

    def test_nullable_fields(self):
        kennel_member = KennelMemberDataModel(self.kennel_id, self.hasher_id)
        kennel_member.save()
        self.assertIsNone(kennel_member.joined)

    def test_kennel_required(self):
        with self.assertRaises(ValueError):
            kennel_member = KennelMemberDataModel(hasher_id=self.hasher_id, joined=self.joined)
            kennel_member.save()

    def test_hasher_required(self):
        with self.assertRaises(ValueError):
            kennel_member = KennelMemberDataModel(kennel_id=self.kennel_id, joined=self.joined)
            kennel_member.save()

    def test_join_persisted(self):
        kennel_member = KennelMemberDataModel(self.kennel_id, self.hasher_id, joined=self.joined)
        kennel_member.save()
        actual = KennelMemberDataModel.get(self.kennel_id, self.hasher_id)
        self.assertEqual(kennel_member, actual)

    def test_members(self):
        for x in range(3):
            for y in range(5):
                KennelMemberDataModel(kennel_id=f'kennel_{x}', hasher_id=f'hasher_{x}{y}', joined=self.joined).save()
        actual = KennelMemberDataModel.members('kennel_2')
        expected = [f'hasher_2{x}' for x in range(5)]
        self.assertListEqual(actual, expected)
