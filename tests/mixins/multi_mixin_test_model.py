from app.models.persistence.base import BaseMeta, BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from app.models.persistence.mixins.version import VersionMixin
from pynamodb.attributes import UnicodeAttribute


class MultiMixinTestModel(TimeStampableMixin, VersionMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'multi_mixin_tests'

    test_id = UnicodeAttribute(hash_key=True)
    field = UnicodeAttribute()
