from app.models.persistence import AlreadyExists
from app.models.persistence.base import BaseMeta, BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from pynamodb.attributes import JSONAttribute, MapAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex


class HasherMotherKennelAttribute(MapAttribute):
    kennel_id = UnicodeAttribute()
    name = UnicodeAttribute()
    acronym = UnicodeAttribute()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__


class HashNameIndex(GlobalSecondaryIndex):
    class Meta(BaseMeta):
        index_name = 'hash_name_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    lower_hash_name = UnicodeAttribute(hash_key=True)
    mother_kennel_name_lower = UnicodeAttribute(range_key=True)


class HasherReferenceModel(MapAttribute):
    hasher_id = UnicodeAttribute()
    hash_name = UnicodeAttribute()

    def is_ref(self, kennel):
        if not isinstance(kennel, HasherDataModel):
            return False
        for attr in self.attribute_values.keys():
            if self.attribute_values[attr] != kennel.attribute_values[attr]:
                return False
        return True


class HasherDataModel(TimeStampableMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'hashers'

    def __init__(self, hash_key=None, range_key=None, **attributes):
        meta_attributes = ['hasher_id']
        try:
            self.__meta_attributes__.extend(meta_attributes)
        except AttributeError:
            self.__meta_attributes__ = meta_attributes
        super().__init__(hash_key, range_key, **attributes)

    hasher_id = UnicodeAttribute(hash_key=True)
    contact_info = JSONAttribute(null=True)
    hash_name = UnicodeAttribute()
    lower_hash_name = UnicodeAttribute()
    mother_kennel = HasherMotherKennelAttribute()
    mother_kennel_name_lower = UnicodeAttribute()
    real_name = UnicodeAttribute(null=True)
    user = UnicodeAttribute(null=True)
    hash_name_index = HashNameIndex()

    def save(self, condition=None, conditional_operator=None, **expected_values):
        matches = self.matching_records(self)
        if matches:
            msg = f'Record with hash name {self.hash_name} with mother kennel {self.mother_kennel} already exists'
            raise AlreadyExists(msg)
        super().save(condition=condition, conditional_operator=conditional_operator, **expected_values)

    def to_ref(self):
        return HasherReferenceModel(hasher_id=self.hasher_id, hash_name=self.hash_name)

    # This method is implemented such that if two hasher records were attempted to be created with the same
    # hash name and mother kennel, they would collide.  It is expected that the same kennel will not have two hashers
    # with the same name.  However, if a hasher is a user they will have a user record and that could further
    # disambiguate this situation, if an existing hash record has a user reference, then it should all work out.
    @classmethod
    def matching_records(cls, record, filter_self=True):
        query_result = cls.hash_name_index.query(record.lower_hash_name,
                                                 cls.mother_kennel_name_lower == record.mother_kennel_name_lower)
        record_attrs = record.attributes()
        results = [result for result in query_result]
        results = [result for result in results if cls._record_match(result.attributes(), record_attrs)]
        if filter_self:
            results = [result for result in results if result.hasher_id != record.hasher_id]
        return results

    @classmethod
    def record_exists(cls, record):
        return cls.count(record.hasher_id) > 0

    @staticmethod
    def _record_match(a, b):
        try:
            return all([a[key] == b[key] for key in a.keys()])
        except KeyError:
            return False
