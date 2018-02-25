import unittest
from app.models.logic.hasher import HasherLogicModel
from app.models.logic.kennel import KennelLogicModel
from app.models.persistence import AlreadyExists
from app.models.persistence.kennel import KennelDataModel, KennelMemberDataModel
from tests.models import logic


class KennelLogicTests(unittest.TestCase):
    def setUp(self):
        self.kennel_id = 'test_id'
        self.name = 'Test_Kennel'
        self.acronym = 'TKH3'
        logic.clean_create_tables([KennelDataModel, KennelMemberDataModel, HasherDataModel])

    def test_init_from_lookup(self):
        KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                        lower_name=self.name.lower(), lower_acronym=self.acronym.lower()).save()
        x = KennelLogicModel.lookup_by_id(self.kennel_id)
        self.assertEqual(self.kennel_id, x.kennel_id)
        self.assertEqual(self.name, x.name)
        self.assertEqual(self.acronym, x.acronym)

    def test_lookup_kennel_doesnt_exist(self):
        with self.assertRaises(KennelDataModel.DoesNotExist):
            KennelLogicModel.lookup_by_id(self.kennel_id)

    def test_create(self):
        actual = KennelLogicModel.create(self.name, self.acronym)
        expected = KennelLogicModel.lookup_by_id(actual.kennel_id)
        self.assertEqual(actual, expected)
        self.assertEqual(actual.name, self.name)
        self.assertEqual(actual.acronym, self.acronym)

    def test_cant_create_same_name(self):
        logic.clean_create_tables([KennelDataModel, ])
        KennelLogicModel.create(self.name, self.acronym)
        with self.assertRaises(AlreadyExists):
            KennelLogicModel.create(self.name, 'xxxhhh')

    def tearDown(self):
        if KennelMemberDataModel.exists():
            KennelMemberDataModel.delete_table()
        if KennelDataModel.exists():
            KennelDataModel.delete_table()


class KennelMembershipTests(unittest.TestCase):
    def setUp(self):
        logic.clean_create_tables([KennelDataModel, KennelMemberDataModel, HasherDataModel])
        self.kennel_a = KennelLogicModel.create('kennel A', 'KAHHH')
        self.kennel_b = KennelLogicModel.create('kennel B', 'KBHHH')
        self.hasher1 = HasherLogicModel.create('Hasher 1', 'kennel A')
        self.hasher2 = 'hasher_2_id'
        self.hasher3 = 'hasher_3_id'
        self.name_a = 'Test_Kennel_A'
        self.acronym_a = 'TKAH3'
        self.name_b = 'Test_Kennel_B'
        self.acronym_b = 'TKBH3'

    def test_create_membership(self):
        KennelLogicModel.create_membership(self.kennel_a, self.hasher1)
        actual = list(KennelMemberDataModel.query(self.kennel_a))[0]
        self.assertEqual(actual.attributes()['kennel_id'], self.kennel_a)
        self.assertEqual(actual.attributes()['hasher_id'], self.hasher1)

    def test_load_members(self):
        a = KennelLogicModel(self.name_a, self.acronym_a, kennel_id=self.kennel_a)
        b = KennelLogicModel(self.name_b, self.acronym_b, kennel_id=self.kennel_b)
        KennelLogicModel.create_membership(a.kennel_id, self.hasher1)
        KennelLogicModel.create_membership(a.kennel_id, self.hasher2)
        KennelLogicModel.create_membership(b.kennel_id, self.hasher3)
        a.load_members()
        b.load_members()
        self.assertListEqual(a.members, [self.hasher1, self.hasher2])
        self.assertListEqual(b.members, [self.hasher3])

    def test_add_member(self):
        a = KennelLogicModel(self.name_a, self.acronym_a, kennel_id=self.kennel_a)
        b = KennelLogicModel(self.name_b, self.acronym_b, kennel_id=self.kennel_b)
        a.add_member(self.hasher1)
        a.add_member(self.hasher2)
        b.add_member(self.hasher3)
        self.assertListEqual(a.members, [self.hasher1, self.hasher2])
        self.assertListEqual(b.members, [self.hasher3])

    def test_add_same_member_twice(self):
        a = KennelLogicModel(self.name_a, self.acronym_a, kennel_id=self.kennel_a)
        a.add_member(self.hasher1)
        with self.assertRaises(AlreadyExists):
            a.add_member(self.hasher1)

    def tearDown(self):
        if KennelMemberDataModel.exists():
            KennelMemberDataModel.delete_table()
        if KennelDataModel.exists():
            KennelDataModel.delete_table()
