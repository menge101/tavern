import geohash as geohasher
from ulid import ulid
from datetime import datetime, timezone
from app.models.persistence import AlreadyExists
from app.models.persistence.location import LocationDataModel
from app.models.logic.base import LogicBase


class LocationLogicModel(LogicBase):
    def __init__(self, name, address1, address2, city, state_province_region, country, postal_code,
                 location_id=None, geohash=None, searchable_name=None, longitude=None, latitude=None,
                 persistence_object=None):
        super().__init__()
        self.geohash = geohash
        self.latitude = latitude
        self.longitude = longitude

        if self.geohash is None:
            if self.latitude is None or self.longitude is None:
                raise ValueError('Either geohash or both latitude and longitude must be provided')
            self.geohash = geohasher.encode(self.latitude, self.longitude)
        if self.latitude is None or self.longitude is None:
            self.latitude, self.longitude = self.decode_geohash()

        self.location_id = ulid() if location_id is None else location_id
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state_province_region = state_province_region
        self.postal_code = postal_code
        self.country = country

        if searchable_name is None:
            self.searchable_name = LocationDataModel.searchable_value(self.name)
        else:
            self.searchable_name = searchable_name

        if persistence_object is None:
            self.persistence_object = LocationDataModel(**self.persistable_attributes())
        else:
            self.persistence_object = persistence_object

    def decode_geohash(self):
        return geohasher.decode(self.geohash)

    @classmethod
    def create(cls, name, address1, address2, city, state_province_region, country, postal_code,
                 location_id=None, geohash=None, longitude=None, latitude=None ):
        location = LocationLogicModel(name, address1, address2, city, state_province_region, country, postal_code,
                                      location_id=location_id, geohash=geohash, longitude=longitude, latitude=latitude)
        location.save()
        return location

    @classmethod
    def lookup_by_name(cls, name):
        result = LocationDataModel.get()
