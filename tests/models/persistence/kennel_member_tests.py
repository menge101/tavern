import unittest
from datetime import datetime, timezone
from app.models.logic.hasher import HasherLogicModel
from app.models.logic.kennel import KennelLogicModel
from app.models.persistence.hasher import HasherDataModel
from app.models.persistence.kennel import KennelMemberDataModel, KennelDataModel
from tests.models import logic


class KennelMemberTests(unittest.TestCase):
    def setUp(self):
        logic.clean_create_tables([KennelDataModel, KennelMemberDataModel, HasherDataModel])
        self.name = 'Test Kennel 1'
        self.acronym = 'TK1H3'
        self.hash_name = 'Testy Hasher'
        kennel = KennelLogicModel.create(self.name, self.acronym)
        self.kennel = kennel.persistence_object
        hasher = HasherLogicModel.create(self.hash_name, kennel)
        self.hasher = hasher.persistence_object
        self.joined = datetime.now(tz=timezone.utc)

    def test_nullable_fields(self):
        kennel_member = KennelMemberDataModel(self.kennel.kennel_id, self.hasher.hasher_id,
                                              kennel_ref=self.kennel.to_ref(), hasher_ref=self.hasher.to_ref())
        kennel_member.save()
        self.assertIsNone(kennel_member.joined)

    def test_kennel_required(self):
        with self.assertRaises(ValueError):
            kennel_member = KennelMemberDataModel(self.kennel.kennel_id, self.hasher.hasher_id,
                                                  hasher=self.hasher.to_ref(), joined=self.joined)
            kennel_member.save()

    def test_hasher_required(self):
        with self.assertRaises(ValueError):
            kennel_member = KennelMemberDataModel(self.kennel.kennel_id, self.hasher.hasher_id,
                                                  kennel_ref=self.kennel.to_ref(), joined=self.joined)
            kennel_member.save()

    def test_join_persisted(self):
        kennel_member = KennelMemberDataModel(self.kennel.kennel_id, self.hasher.hasher_id,
                                              hasher_ref=self.hasher.to_ref(), kennel_ref=self.kennel.to_ref(),
                                              joined=self.joined)
        kennel_member.save()
        actual = KennelMemberDataModel.get(self.kennel.kennel_id, self.hasher.hasher_id)
        self.assertEqual(kennel_member, actual)

    def test_members(self):
        kennels = list()
        hashers = list()
        for x in range(3):
            kennel_model = KennelLogicModel.create(f'kennel_{x}', f'TK{x}H3')
            kennel = kennel_model.persistence_object
            kennels.append(kennel)
            for y in range(5):
                hasher_model = HasherLogicModel.create(f'hasher_{x}{y}', kennel_model)
                hasher = hasher_model.persistence_object
                hashers.append(hasher)
                membership = KennelMemberDataModel(kennel.kennel_id, hasher.hasher_id, hasher_ref=hasher.to_ref(), kennel_ref=kennel.to_ref())
                membership.save()
        actual = KennelMemberDataModel.members(kennels[1].kennel_id)
        actual_names = [hasher.hash_name for hasher in actual]
        expected_names = [f'hasher_1{x}' for x in range(5)]
        self.assertListEqual(actual_names, expected_names)
