from app.models.persistence.base import BaseMeta, BaseModel
from app.models.persistence.event import EventReferenceModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from pynamodb.attributes import MapAttribute, NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute


class LocationReferenceModel(MapAttribute):
    geohash = UnicodeAttribute()
    name = UnicodeAttribute()
    address1 = UnicodeAttribute()
    address2 = UnicodeAttribute()
    city = UnicodeAttribute()
    state_province_region = UnicodeAttribute()
    postal_code = UnicodeAttribute()
    latitude = NumberAttribute()
    longitude = NumberAttribute()

    def is_ref_of(self, location):
        if not isinstance(location, LocationDataModel):
            return False
        for attr in self.attribute_values.keys():
            if self.attribute_values[attr] != location.attribute_values[attr]:
                return False
        return True

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__


class LocationDataModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'locations'

    geohash = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    searchable_name = UnicodeAttribute(range_key=True)
    address1 = UnicodeAttribute()
    address2 = UnicodeAttribute()
    city = UnicodeAttribute()
    state_province_region = UnicodeAttribute()
    postal_code = UnicodeAttribute()
    longitude = NumberAttribute()
    latitude = NumberAttribute()

    def to_ref(self):
        return super().to_ref(LocationReferenceModel)


class EventLocationDataModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'event_locations'

    geohash = UnicodeAttribute(hash_key=True)
    start_time = UTCDateTimeAttribute(range_key=True)
    location_ref = LocationReferenceModel()
    event_ref = EventReferenceModel()
