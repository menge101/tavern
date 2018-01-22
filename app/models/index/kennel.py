from app.models.persistence.base import BaseModel
from pynamodb.attributes import JSONAttribute, UnicodeAttribute


class KennelIndexModel(BaseModel):
    class Meta:
        table_name = 'kennel_index'

    kennel_id = UnicodeAttribute()
    foreign_data = JSONAttribute()
