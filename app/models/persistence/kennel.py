from app.models.persistence.base import BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from pynamodb.attributes import JSONAttribute, ListAttribute, UnicodeAttribute


class KennelDataModel(TimeStampableMixin, BaseModel):
    class Meta:
        table_name = 'kennels'

    kennel_id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    acronym = UnicodeAttribute()
    region = ListAttribute(null=True)
    events = ListAttribute(null=True)
    members = ListAttribute(null=True)
    officers = JSONAttribute(null=True)
    contact = JSONAttribute(null=True)
    webpage = UnicodeAttribute(null=True)
    facebook = UnicodeAttribute(null=True)
    founding = JSONAttribute(null=True)
    description = UnicodeAttribute(null=True)
