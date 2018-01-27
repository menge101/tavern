from app.models.persistence.base import BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from pynamodb.attributes import ListAttribute, UnicodeAttribute, UTCDateTimeAttribute


class EventDataModel(TimeStampableMixin, BaseModel):
    class Meta:
        table_name = 'events'

    event_id = UnicodeAttribute(hash_key=True)
    hares = ListAttribute()
    name = UnicodeAttribute()
    description = UnicodeAttribute()
    kennels = ListAttribute()
    type = UnicodeAttribute()
    start_time = UTCDateTimeAttribute()
    end_time = UTCDateTimeAttribute(null=True)
    start_location = UnicodeAttribute()
    trails = ListAttribute(null=True)
