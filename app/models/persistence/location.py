import base32_crockford as b32
import regex
from app.models.persistence import AlreadyExists
from app.models.persistence.base import BaseMeta, BaseModel
from app.models.persistence.event import EventReferenceModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from pynamodb.attributes import MapAttribute, NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex


class LocationReferenceModel(MapAttribute):
    geohash = UnicodeAttribute()
    name = UnicodeAttribute()
    address1 = UnicodeAttribute()
    address2 = UnicodeAttribute()
    city = UnicodeAttribute()
    state_province_region = UnicodeAttribute()
    postal_code = UnicodeAttribute()
    country = UnicodeAttribute()
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


class LocationNameIndex(GlobalSecondaryIndex):
    class Meta(BaseMeta):
        index_name = 'location_name_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    searchable_name = UnicodeAttribute(hash_key=True)
    geohash = UnicodeAttribute(range_key=True)


class LongitudeLatitudeIndex(GlobalSecondaryIndex):
    class Meta(BaseMeta):
        index_name = 'longitude_latitude_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    longitude = NumberAttribute(hash_key=True)
    latitude = NumberAttribute(range_key=True)


class SearchableNameIndex(GlobalSecondaryIndex):
    class Meta(BaseMeta):
        index_name = 'searchable_name_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    searchable_name_prefix = UnicodeAttribute(hash_key=True)
    searchable_name_suffix = UnicodeAttribute(range_key=True)


class LocationDataModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'locations'

    __before_save_hooks__ = ['split_searchable_name']

    def __init__(self, hash_key=None, range_key=None, **attributes):
        meta_attributes = ['location_id', 'searchable_name_prefix', 'searchable_name_suffix']
        try:
            self.__meta_attributes__.extend(meta_attributes)
        except AttributeError:
            self.__meta_attributes__ = meta_attributes

        try:
            self.before_save_hooks.extend(self.__before_save_hooks__)
        except AttributeError:
            self.before_save_hooks = self.__before_save_hooks__
        super().__init__(hash_key, range_key, **attributes)

    location_id = UnicodeAttribute(hash_key=True)
    geohash = UnicodeAttribute()
    name = UnicodeAttribute()
    searchable_name = UnicodeAttribute()
    searchable_name_prefix = UnicodeAttribute()
    searchable_name_suffix = UnicodeAttribute()
    address1 = UnicodeAttribute()
    address2 = UnicodeAttribute()
    city = UnicodeAttribute()
    state_province_region = UnicodeAttribute()
    country = UnicodeAttribute()
    postal_code = UnicodeAttribute()
    longitude = NumberAttribute()
    latitude = NumberAttribute()
    location_name_index = LocationNameIndex()
    long_lat_index = LongitudeLatitudeIndex()
    searchable_name_index = SearchableNameIndex()

    def save(self, condition=None, conditional_operator=None, **expected_values):
        matches = self.matching_records_by_proximity(self)
        if matches:
            msg = f'Record with name {self.name} already exists in the same proximity.'
            raise AlreadyExists(msg)
        super().save(condition=condition, conditional_operator=conditional_operator, **expected_values)

    def split_searchable_name(self):
        self.searchable_name_prefix = self.searchable_name[0:3]
        self.searchable_name_suffix = self.searchable_name[3:]

    def to_ref(self):
        return super().to_ref(LocationReferenceModel)

    @classmethod
    def generate_searchable_address(cls, address1, address2, city, state_province_region, postal_code, country):
        add_list = [address1, address2, city, state_province_region, postal_code, country]
        return regex.sub(r'\W', '', ''.join(add_list).lower())

    @classmethod
    def matching_records_by_proximity(cls, record):
        search_geohash = record.geohash[:-1]
        low = search_geohash + '0'
        high = b32.encode(b32.decode(search_geohash) + 1) + '0'
        return cls.location_name_index.count(record.searchable_name,
                                             range_key_condition=cls.geohash.between(low, high),
                                             filter_condition=cls.location_id != record.location_id)


class EventLocationDataModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'event_locations'

    geohash = UnicodeAttribute(hash_key=True)
    start_time = UTCDateTimeAttribute(range_key=True)
    location_ref = LocationReferenceModel()
    event_ref = EventReferenceModel()
