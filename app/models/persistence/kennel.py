from pynamodb.attributes import JSONAttribute, ListAttribute, UnicodeAttribute
from app.models.persistence.base import BaseModel


class KennelIndexModel(BaseModel):
    class Meta:
        table_name = 'kennel_index'

    kennel_id = UnicodeAttribute()
    foreign_data = JSONAttribute()


class KennelDataModel(BaseModel):
    class Meta:
        table_name = 'kennels'

    kennel_id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    acronym = UnicodeAttribute()
    region = ListAttribute(null=True)
    events = ListAttribute(null=True)
    members = ListAttribute(null=True)
    officers = JSONAttribute(null=True)