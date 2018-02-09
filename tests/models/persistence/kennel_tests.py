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
        kennel = KennelDataModel(self.kennel_id, name=self.name, lower_name=self.name.lower(),
                                 acronym=self.acronym, lower_acronym=self.acronym.lower())
        self.assertIsNone(kennel.region)
        self.assertIsNone(kennel.contact)
        self.assertIsNone(kennel.webpage)
        self.assertIsNone(kennel.facebook)
        self.assertIsNone(kennel.founding)
        self.assertIsNone(kennel.description)

    def test_id_required(self):
        kennel = KennelDataModel(name=self.name, lower_name=self.name.lower(),
                                 acronym=self.acronym, lower_acronym=self.acronym.lower())
        with self.assertRaises(ValueError):
            kennel.save()

    def test_name_required(self):
        kennel = KennelDataModel(self.kennel_id, lower_name=self.name.lower(),
                                 acronym=self.acronym, lower_acronym=self.acronym.lower())
        with self.assertRaises(ValueError):
            kennel.save()

    def test_lower_name_required(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                                 lower_acronym=self.acronym.lower())
        with self.assertRaises(ValueError):
            kennel.save()

    def test_acronym_required(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, lower_name=self.name.lower(),
                                 lower_acronym=self.acronym.lower())
        with self.assertRaises(ValueError):
            kennel.save()

    def test_lower_acronym_required(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, lower_name=self.name.lower(),
                                 acronym=self.acronym)
        with self.assertRaises(ValueError):
            kennel.save()

    def test_timestamps(self):
        time = datetime.now(timezone.utc)
        with freeze_time(time):
            kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                                     lower_name=self.name.lower(), lower_acronym=self.acronym.lower())
            kennel.save()
            self.assertEqual(kennel.modified_at, time)
            self.assertEqual(kennel.created_at, time)

    def test_all_fields(self):
        KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym, lower_name=self.name.lower(),
                        lower_acronym=self.acronym.lower(), region=self.region, contact=self.contact,
                        webpage=self.webpage, facebook=self.facebook, founding=self.founding,
                        description=self.description).save()

        kennel = KennelDataModel.get(self.kennel_id)
        self.assertEqual(kennel.region, self.region)
        self.assertEqual(kennel.contact, self.contact)
        self.assertEqual(kennel.webpage, self.webpage)
        self.assertEqual(kennel.facebook, self.facebook)
        self.assertEqual(kennel.founding, self.founding)
        self.assertEqual(kennel.description, self.description)
        self.assertEqual(kennel.lower_name, self.name.lower())
        self.assertEqual(kennel.lower_acronym, self.acronym.lower())

    def test_record_exists(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                                 lower_name=self.name.lower(), lower_acronym=self.acronym.lower())
        kennel.save()
        self.assertTrue(KennelDataModel.record_exists(kennel))

    def test_record_does_not_exist(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                                 lower_name=self.name.lower(), lower_acronym=self.acronym.lower())
        self.assertFalse(KennelDataModel.record_exists(kennel))

    def test_matching_records_does_not_exist(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, lower_name=self.name.lower(),
                                 acronym=self.acronym, lower_acronym=self.acronym.lower())
        self.assertListEqual(KennelDataModel.matching_records(kennel), list())

    def test_matching_record_filtering_self(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                                 lower_name=self.name.lower(), lower_acronym=self.acronym.lower())
        kennel.save()
        self.assertListEqual(KennelDataModel.matching_records(kennel), list())

    def test_matching_record_not_filtering_self(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                                 lower_name=self.name.lower(), lower_acronym=self.acronym.lower())
        kennel.save()
        self.assertListEqual(KennelDataModel.matching_records(kennel, False), [kennel])

    def test_matching_records_multiple_close_matches(self):
        KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                        lower_name=self.name.lower(), lower_acronym=self.acronym.lower()).save()
        kennel = KennelDataModel('different_id', name='Thinking Kennel', acronym=self.acronym,
                                 lower_name='thinking kennel', lower_acronym=self.acronym.lower())
        kennel.save()
        KennelDataModel('different_id_2', name='Throwing Kennel', acronym=self.acronym,
                        lower_name='throwing kennel', lower_acronym=self.acronym.lower()).save()
        match = KennelDataModel('match_kennel', name='Thinking Kennel', acronym=self.acronym,
                                lower_name='thinking kennel', lower_acronym=self.acronym.lower())
        x = KennelDataModel.matching_records(match)
        self.assertListEqual(x, [kennel])

    def test_matching_record_by_name(self):
        kennel = KennelDataModel(self.kennel_id, name=self.name, acronym=self.acronym,
                                 lower_name=self.name.lower(), lower_acronym=self.acronym.lower())
        kennel.save()
        kennel2 = KennelDataModel('new_id', name=self.name, acronym='ABCH3',
                                  lower_name=self.name.lower(), lower_acronym='abch3')
        with self.assertRaises(AlreadyExists):
            kennel2.save()

    def test_save_with_existing_record(self):
        KennelDataModel('kennel1', name=self.name, acronym=self.acronym,
                        lower_name=self.name.lower(), lower_acronym=self.acronym.lower()).save()
        with self.assertRaises(AlreadyExists):
            KennelDataModel('kennel2', name=self.name, acronym=self.acronym,
                            lower_name=self.name.lower(), lower_acronym=self.acronym.lower()).save()

    def test_save_same_record_twice(self):
        start = KennelDataModel('kennel1', name=self.name, acronym=self.acronym,
                                lower_name=self.name.lower(), lower_acronym=self.acronym.lower())
        start.save()
        start.save()
        self.assertTrue(KennelDataModel.record_exists(start))
