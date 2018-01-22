from app.mixins.timestamps import TimeStampableMixin
from app.models.persistence.base import BaseModel
from pynamodb.attributes import UnicodeAttribute


class TimestampTestModel(TimeStampableMixin, BaseModel):
    class Meta:
        table_name = 'timestamp_tests'

    test_id = UnicodeAttribute(hash_key=True)
    field = UnicodeAttribute()
