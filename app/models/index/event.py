from pynamodb.attributes import JSONAttribute, UnicodeAttribute
from app.models.persistence.base import BaseModel


class EventIndexModel(BaseModel):
    class Meta:
        table_name = 'event_index'

    event_id = UnicodeAttribute()
    foreign_data = JSONAttribute()
