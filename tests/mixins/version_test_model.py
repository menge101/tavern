from app.models.persistence.mixins.version import VersionMixin
from app.models.persistence.base import BaseModel
from pynamodb.attributes import UnicodeAttribute


class VersionTestModel(VersionMixin, BaseModel):
    class Meta:
        table_name = 'version_tests'

    test_id = UnicodeAttribute(hash_key=True)
    field1 = UnicodeAttribute()
    field2 = UnicodeAttribute(null=True)
