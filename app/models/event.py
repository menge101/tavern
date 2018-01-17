from pynamodb.attributes import JSONAttribute, ListAttribute, UnicodeAttribute, UTCDateTimeAttribute
from app.models.base import BaseModel


class EventIndexModel(BaseModel):
    class Meta:
        table_name = 'event_index'

    event_id = UnicodeAttribute()
    foreign_data = JSONAttribute()


class EventDataModel(BaseModel):
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
