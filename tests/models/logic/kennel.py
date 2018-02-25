import unittest
from app.models.logic.hasher import HasherLogicModel
from app.models.logic.kennel import KennelLogicModel
from app.models.persistence import AlreadyExists
from app.models.persistence.hasher import HasherDataModel
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

    def test_init_from_ref(self):
        orig = KennelLogicModel.create(self.name, self.acronym)
        ref = orig.persistence_object.to_ref()
        lookup = KennelLogicModel.lookup_by_ref(ref)
        self.assertEqual(orig, lookup)

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
        self.hasher1 = HasherLogicModel.create('Hasher 1', self.kennel_a)
        self.hasher2 = HasherLogicModel.create('Hasher 2', self.kennel_a)
        self.hasher3 = HasherLogicModel.create('Hasher 3', self.kennel_b)

    def test_create_membership(self):
        KennelLogicModel.create_membership(self.kennel_a, self.hasher1)
        actual = list(KennelMemberDataModel.query(self.kennel_a.kennel_id))[0]
        self.assertEqual(actual.attributes()['kennel_id'], self.kennel_a.kennel_id)
        self.assertEqual(actual.attributes()['hasher_id'], self.hasher1.hasher_id)

    def test_load_members(self):
        KennelLogicModel.create_membership(self.kennel_a, self.hasher1)
        KennelLogicModel.create_membership(self.kennel_a, self.hasher2)
        KennelLogicModel.create_membership(self.kennel_b, self.hasher3)
        self.kennel_a.load_members()
        self.kennel_b.load_members()
        x = self.kennel_a.members
        self.assertListEqual(x, [self.hasher1.persistence_object.to_ref(), self.hasher2.persistence_object.to_ref()])
        self.assertListEqual(self.kennel_b.members, [self.hasher3.persistence_object.to_ref()])

    def test_add_member(self):
        self.kennel_a.add_member(self.hasher1)
        self.kennel_a.add_member(self.hasher2)
        self.kennel_b.add_member(self.hasher3)
        self.assertListEqual(self.kennel_a.members,
                             [self.hasher1.persistence_object.to_ref(), self.hasher2.persistence_object.to_ref()])
        self.assertListEqual(self.kennel_b.members, [self.hasher3.persistence_object.to_ref()])

    def test_add_same_member_twice(self):
        self.kennel_a.add_member(self.hasher1)
        with self.assertRaises(AlreadyExists):
            self.kennel_a.add_member(self.hasher1)

    def test_list_members(self):
        self.kennel_a.add_member(self.hasher1)
        self.kennel_a.add_member(self.hasher2)
        self.kennel_b.add_member(self.hasher3)
        self.assertListEqual(KennelLogicModel.list_members(self.kennel_a),
                             [self.hasher1.persistence_object.to_ref(), self.hasher2.persistence_object.to_ref()])
        self.assertListEqual(KennelLogicModel.list_members(self.kennel_b), [self.hasher3.persistence_object.to_ref()])

    def tearDown(self):
        if KennelMemberDataModel.exists():
            KennelMemberDataModel.delete_table()
        if KennelDataModel.exists():
            KennelDataModel.delete_table()
