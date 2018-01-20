from pynamodb.attributes import JSONAttribute, UnicodeAttribute
from app.models.persistence.base import BaseModel


class KennelIndexModel(BaseModel):
    class Meta:
        table_name = 'kennel_index'

    kennel_id = UnicodeAttribute()
    foreign_data = JSONAttribute()
