import unittest
from datetime import datetime, timezone
from app.models.persistence import AlreadyExists
from app.models.persistence.kennel import KennelDataModel
from freezegun import freeze_time


class KennelTests(unittest.TestCase):
    def setUp(self):
        self.kennel_id = 'test_id'
        self.name = 'Test_Kennel'
        self.acronym = 'TKH3'
        self.region = ['1.1', '1.2', '2.2', '2.1']
        self.contact = [{'name': 'test person', 'phone': '4445556666', 'email': 'atestemail@test.com'}]
        self.facebook = 'http://www.facebook.com/groups/test_kennel'
        self.webpage = 'http://www.testkennel.com'
        self.founding = {'founder': 'G', 'first trail': '1/1/1930'}
        self.description = 'A test kennel'
        if KennelDataModel.exists():
            KennelDataModel.delete_table()
        KennelDataModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def tearDown(self):
        if KennelDataModel.exists():
            KennelDataModel.delete_table()

    def test_nullable_fields(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        self.assertIsNone(kennel.region)
        self.assertIsNone(kennel.contact)
        self.assertIsNone(kennel.webpage)
        self.assertIsNone(kennel.facebook)
        self.assertIsNone(kennel.founding)
        self.assertIsNone(kennel.description)

    def test_id_required(self):
        kennel = KennelDataModel(name=self.name, acronym=self.acronym)
        with self.assertRaises(ValueError):
            kennel.save()

    def test_name_required(self):
        with self.assertRaises(ValueError):
            KennelDataModel(self.kennel_id, acronym=self.acronym)

    def test_acronym_required(self):
        with self.assertRaises(ValueError):
            KennelDataModel(self.kennel_id, name=self.name)

    def test_timestamps(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
            kennel.save()
            self.assertEqual(kennel.modified_at, time)
            self.assertEqual(kennel.created_at, time)

    def test_all_fields(self):
        KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym, region=self.region, contact=self.contact,
                        webpage=self.webpage, facebook=self.facebook, founding=self.founding,
                        description=self.description).save()

        kennel = KennelDataModel.get(self.kennel_id)
        self.assertEqual(kennel.region, self.region)
        self.assertEqual(kennel.contact, self.contact)
        self.assertEqual(kennel.webpage, self.webpage)
        self.assertEqual(kennel.facebook, self.facebook)
        self.assertEqual(kennel.founding, self.founding)
        self.assertEqual(kennel.description, self.description)
        self.assertEqual(kennel.searchable_name, kennel.searchable_value(kennel.name))
        self.assertEqual(kennel.searchable_acronym, kennel.searchable_value(kennel.acronym))

    def test_record_exists(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        kennel.save()
        self.assertTrue(KennelDataModel.record_exists(kennel))

    def test_record_does_not_exist(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        self.assertFalse(KennelDataModel.record_exists(kennel))

    def test_matching_records_does_not_exist(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        self.assertListEqual(KennelDataModel.matching_records(kennel), list())

    def test_matching_record_filtering_self(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        kennel.save()
        self.assertListEqual(KennelDataModel.matching_records(kennel), list())

    def test_matching_record_not_filtering_self(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        kennel.save()
        self.assertListEqual(KennelDataModel.matching_records(kennel, False), [kennel])

    def test_matching_records_multiple_close_matches(self):
        KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym).save()
        kennel = KennelDataModel('different_id', name='Thinking Kennel', acronym=self.acronym)
        kennel.save()
        KennelDataModel('different_id_2', name='Throwing Kennel', acronym=self.acronym).save()
        match = KennelDataModel('match_kennel', name='Thinking Kennel', acronym=self.acronym)
        x = KennelDataModel.matching_records(match)
        self.assertListEqual(x, [kennel])

    def test_matching_record_by_name(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        kennel.save()
        kennel2 = KennelDataModel('new_id', name=self.name, acronym='ABCH3')
        with self.assertRaises(AlreadyExists):
            kennel2.save()

    def test_save_with_existing_record(self):
        KennelDataModel('kennel1', name=self.name, acronym=self.acronym).save()
        with self.assertRaises(AlreadyExists):
            KennelDataModel('kennel2', name=self.name, acronym=self.acronym).save()

    def test_save_same_record_twice(self):
        start = KennelDataModel('kennel1', name=self.name, acronym=self.acronym)
        start.save()
        start.save()
        self.assertTrue(KennelDataModel.record_exists(start))

    def test_to_ref(self):
        ref = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym).to_ref()
        self.assertEqual(ref.acronym, self.acronym)
        self.assertEqual(ref.kennel_id, self.kennel_id)
        self.assertEqual(ref.name, self.name)
        self.assertListEqual(list(ref.attribute_values.keys()), ['kennel_id', 'name', 'acronym'])

    def test_is_ref(self):
        mdl = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        ref = mdl.to_ref()
        self.assertTrue(ref.is_ref(mdl))

    def test_is_not_ref(self):
        mdl = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        mdl2 = KennelDataModel('diff', name=self.name, acronym=self.acronym)
        ref = mdl2.to_ref()
        self.assertFalse(ref.is_ref(mdl))

    def test_is_not_ref_diff_class(self):
        mdl = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        mdl2 = KennelDataModel('diff', name=self.name, acronym=self.acronym)
        ref = mdl2.to_ref()
        self.assertFalse(ref.is_ref(mdl.to_ref()))

    def test_on_init_searchable_name(self):
        k = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        self.assertEqual(k.searchable_name, k.searchable_value(k.name))

    def test_on_init_searchable_acronym(self):
        k = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        self.assertEqual(k.searchable_acronym, k.searchable_value(k.acronym))

    def test_on_save_searchable_name(self):
        k = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        new_name = 'Cheese'
        k.name = new_name
        k.save()
        k.refresh()
        self.assertEqual(k.searchable_name, k.searchable_value(new_name))

    def test_on_save_searchable_acronym(self):
        k = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        new_acronym = 'CKH3'
        k.acronym = new_acronym
        k.save()
        k.refresh()
        self.assertEqual(k.searchable_acronym, k.searchable_value(new_acronym))

    def test_update_searchable_name(self):
        k = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        k.save()
        new_name = 'Cheese'
        k.add_update_action('name', 'set', new_name)
        k.update()
        k.refresh()
        self.assertEqual(k.searchable_name, k.searchable_value(new_name))

    def test_update_searchable_acronym(self):
        k = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym)
        k.save()
        new_acronym = 'CHEH3'
        k.add_update_action('acronym', 'set', new_acronym)
        k.update()
        k.refresh()
        self.assertEqual(k.searchable_acronym, k.searchable_value(new_acronym))
