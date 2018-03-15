import unittest
from app.models.persistence.base import BaseMeta, BaseModel
from pynamodb.attributes import UnicodeAttribute


class BaseTestModel(BaseModel):
    class Meta(BaseMeta):
        table_name = 'base'

    hash_key = UnicodeAttribute(hash_key=True)
    range_key = UnicodeAttribute(range_key=True)


class BaseTests(unittest.TestCase):
    def test_searchable_value(self):
        names = ['Cheesy Grits', 'Cheesy  Grits', 'cheesy grits', 'Cheesy grits']
        norms = [BaseTestModel.searchable_value(name) for name in names]
        booleans = [name == 'cheesygrits' for name in norms]
        self.assertTrue(all(booleans))
