import unittest
from app.models.logic.base import LogicBase


class BaseLogicTests(unittest.TestCase):
    def setUp(self):
        self.base = LogicBase()

    def test_eq_with_other_class(self):
        with self.assertRaises(NotImplementedError):
            self.base == '1'

    def test_eq_with_same_class(self):
        self.assertEqual(self.base, LogicBase())

    def test_unpersistable_not_in_persistable(self):
        attrs = self.base.persistable_attributes()
        for attr in self.base.__unpersistable_attributes__:
            self.assertNotIn(attr, attrs)

    def test_reload_from_persistence(self):
        with self.assertRaises(ValueError):
            self.base.reload_from_persistence()
