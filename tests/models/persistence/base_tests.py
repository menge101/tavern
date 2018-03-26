import unittest
from app.models.persistence.base import BaseMeta, BaseModel
from pynamodb.attributes import ListAttribute, NumberAttribute, UnicodeAttribute, UnicodeSetAttribute


class BaseTestModel(BaseModel):
    __update_action_hooks__ = {'set': {'non_key_value': 'test_hook_action_generation'}}

    class Meta(BaseMeta):
        table_name = 'base'

    def __init__(self, hash_key=None, range_key=None, **attributes):
        self.assign_or_update('update_action_hooks', __class__.__update_action_hooks__)
        super().__init__(hash_key, range_key, **attributes)

    hash_key = UnicodeAttribute(hash_key=True)
    range_key = UnicodeAttribute(range_key=True)
    hook_attribute = UnicodeAttribute(null=True)
    list_attribute = ListAttribute(default=list())
    non_key_value = UnicodeAttribute()
    numeric_value = NumberAttribute(null=True)
    unicode_set = UnicodeSetAttribute(default=set())

    def test_hook_action_generation(self, value):
        return [BaseTestModel.hook_attribute.set(value)]


class BaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if BaseTestModel.exists():
            BaseTestModel.delete_table()

    def setUp(self):
        BaseTestModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def tearDown(self):
        if BaseTestModel.exists():
            BaseTestModel.delete_table()

    @classmethod
    def tearDownClass(cls):
        if BaseTestModel.exists():
            BaseTestModel.delete_table()

    def test_searchable_value(self):
        names = ['Cheesy Grits', 'Cheesy  Grits', 'cheesy grits', 'Cheesy grits']
        norms = [BaseTestModel.searchable_value(name) for name in names]
        booleans = [name == 'cheesygrits' for name in norms]
        self.assertTrue(all(booleans))

    def test_clear_update_list(self):
        b = BaseTestModel('a', 'b', non_key_value='c')
        self.assertListEqual(list(), b.update_actions)
        b.add_update_action('non_key_value', 'set', 'd')
        b.clear_update_set()
        self.assertListEqual(list(), b.update_actions)

    def test_update_hash_key(self):
        b = BaseTestModel('a', 'b', non_key_value='c')
        self.assertListEqual(list(), b.update_actions)
        with self.assertRaises(ValueError):
            b.add_update_action('hash_key', 'set', 'd')

    def test_update_range_key(self):
        b = BaseTestModel('a', 'b', non_key_value='c')
        self.assertListEqual(list(), b.update_actions)
        with self.assertRaises(ValueError):
            b.add_update_action('range_key', 'set', 'd')

    def test_no_updates(self):
        b = BaseTestModel('a', 'b', non_key_value='c')
        self.assertListEqual(list(), b.update_actions)
        with self.assertRaises(ValueError):
            b.update()

    def test_double_update(self):
        b = BaseTestModel('a', 'b', non_key_value='c')
        self.assertListEqual(list(), b.update_actions)
        b.add_update_action('non_key_value', 'set', 'd')
        expected = [str(BaseTestModel.non_key_value.set('d')), str(BaseTestModel.hook_attribute.set('d'))]
        actual = [str(thing) for thing in b.update_actions]
        self.assertListEqual(actual, expected)
        b.update()
        b.refresh()
        with self.assertRaises(ValueError):
            b.update()

    def test_add_update_set(self):
        b = BaseTestModel('a', 'b', non_key_value='c')
        self.assertListEqual(list(), b.update_actions)
        b.add_update_action('non_key_value', 'set', 'd')
        expected = [str(BaseTestModel.non_key_value.set('d')), str(BaseTestModel.hook_attribute.set('d'))]
        actual = [str(thing) for thing in b.update_actions]
        self.assertListEqual(actual, expected)
        b.update()
        b.refresh()
        self.assertEqual(b.non_key_value, 'd')
        self.assertEqual(b.hook_attribute, 'd')

    def test_add_update_remove(self):
        b = BaseTestModel('a', 'b', non_key_value='c')
        self.assertListEqual(list(), b.update_actions)
        b.add_update_action('non_key_value', 'remove')
        expected = str(BaseTestModel.non_key_value.remove())
        actual = [str(thing) for thing in b.update_actions]
        self.assertListEqual(actual, [expected])
        b.update()
        b.refresh()
        self.assertIsNone(b.non_key_value)

    def test_add_update_add_string(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=3)
        self.assertListEqual(list(), b.update_actions)
        with self.assertRaises(ValueError):
            b.add_update_action('non_key_value', 'add', 'r')

    def test_add_update_add_numeric(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=3)
        self.assertListEqual(list(), b.update_actions)
        b.add_update_action('numeric_value', 'add', 1)
        expected = str(BaseTestModel.numeric_value.add(1))
        actual = [str(thing) for thing in b.update_actions]
        self.assertListEqual(actual, [expected])
        b.update()
        b.refresh()
        self.assertEqual(b.numeric_value, 1)

    def test_add_update_add_set(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, unicode_set={'a', 'b', 'c'})
        self.assertListEqual(list(), b.update_actions)
        b.add_update_action('unicode_set', 'add', {'stuff'})
        expected = str(BaseTestModel.unicode_set.add({'stuff'}))
        actual = [str(thing) for thing in b.update_actions]
        self.assertListEqual(actual, [expected])
        b.update()
        b.refresh()
        self.assertSetEqual(b.unicode_set, {'stuff'})

    def test_add_update_delete(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, unicode_set={'a', 'b', 'c'})
        self.assertListEqual(list(), b.update_actions)
        b.add_update_action('unicode_set', 'delete', {'a'})
        expected = str(BaseTestModel.unicode_set.delete({'a'}))
        actual = [str(thing) for thing in b.update_actions]
        self.assertListEqual(actual, [expected])
        b.update()
        b.refresh()
        self.assertIsNone(b.unicode_set)

    def test_add_update_append(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, list_attribute=['a'])
        self.assertListEqual(list(), b.update_actions)
        with self.assertRaises(ValueError):
            b.add_update_action('list_attribute', 'append', ['b'])

    def test_assign_or_extend_assign(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, list_attribute=['a'])
        b.assign_or_extend('cheese', ['a', 'b', 'c'])
        self.assertListEqual(b.cheese, ['a', 'b', 'c'])

    def test_assign_or_extend_extend(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, list_attribute=['a'])
        b.assign_or_extend('list_attribute', ['b', 'c'])
        self.assertListEqual(b.list_attribute, ['a', 'b', 'c'])

    def test_assign_or_extend_non_list_value(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, list_attribute=['a'])
        with self.assertRaises(ValueError):
            b.assign_or_extend('cheese', {'a': 1, 'b': 2})

    def test_assign_or_update_assign(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, list_attribute=['a'])
        b.assign_or_update('cheese', {'a': 1, 'b': 2})
        self.assertDictEqual(b.cheese, {'a': 1, 'b': 2})

    def test_assign_or_update_update(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, list_attribute=['a'])
        b.assign_or_update('cheese', {'a': 1, 'b': 2})
        b.assign_or_update('cheese', {'b': 3, 'c': 4})
        self.assertDictEqual(b.cheese, {'a': 1, 'b': 3, 'c': 4})

    def test_assign_or_update_non_dict_value(self):
        b = BaseTestModel('a', 'b', non_key_value='c', numeric_value=1, list_attribute=['a'])
        with self.assertRaises(ValueError):
            b.assign_or_update('cheese', ['a', 1, 'b', 2])
