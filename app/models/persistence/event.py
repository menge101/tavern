from app.models.persistence.base import BaseMeta, BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from pynamodb.attributes import ListAttribute, MapAttribute, UnicodeAttribute, UTCDateTimeAttribute


class EventReferenceModel(MapAttribute):
    event_id = UnicodeAttribute()
    hares = ListAttribute()
    name = UnicodeAttribute()
    description = UnicodeAttribute()
    kennels = ListAttribute()
    start_time = UTCDateTimeAttribute()
    start_location = UnicodeAttribute()

    def is_ref_of(self, event):
        if not isinstance(event, EventDataModel):
            return False
        for attr in self.attribute_values.keys():
            if self.attribute_values[attr] != event.attribute_values[attr]:
                return False
        return True

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__


class EventDataModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'events'

    event_id = UnicodeAttribute(hash_key=True)
    hares = ListAttribute()
    name = UnicodeAttribute()
    description = UnicodeAttribute()
    kennels = ListAttribute()
    type = UnicodeAttribute()
    start_time = UTCDateTimeAttribute(range_key=True)
    end_time = UTCDateTimeAttribute(null=True)
    start_location = UnicodeAttribute()
    trails = ListAttribute(null=True)

    def to_ref(self):
        valid_keys = [key for key in EventReferenceModel.__dict__.keys() if not key.startswith('_')]
        return EventReferenceModel(**{k: v for k, v in self.attributes().items() if k in valid_keys})


class HareEventDataModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'hare_events'

    hasher_id = UnicodeAttribute(hash_key=True)
    event_id = UnicodeAttribute()
    start_time = UTCDateTimeAttribute(range_key=True)
    event_ref = EventReferenceModel()


class KennelEventDataModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'kennel_events'

    kennel_id = UnicodeAttribute(hash_key=True)
    event_id = UnicodeAttribute()
    start_time = UTCDateTimeAttribute(range_key=True)
    event_ref = EventReferenceModel()
