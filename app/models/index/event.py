from app.models.persistence.base import BaseModel
from pynamodb.attributes import JSONAttribute, UnicodeAttribute


class EventIndexModel(BaseModel):
    class Meta:
        table_name = 'event_index'

    event_id = UnicodeAttribute()
    foreign_data = JSONAttribute()
