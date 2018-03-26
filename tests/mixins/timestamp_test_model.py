from app.models.persistence.base import BaseMeta, BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from pynamodb.attributes import UnicodeAttribute


class TimestampTestModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'timestamp_tests'

    test_id = UnicodeAttribute(hash_key=True)
    field = UnicodeAttribute()
