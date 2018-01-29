from app.models.persistence.base import BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from app.models.persistence.mixins.version import VersionMixin
from pynamodb.attributes import JSONAttribute, ListAttribute, NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute


class KennelDataModel(TimeStampableMixin, VersionMixin, BaseModel):
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
    next_trail_number = NumberAttribute(null=True)
