from app.models.persistence import AlreadyExists
from app.models.persistence.base import BaseMeta, BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from app.models.persistence.mixins.version import VersionMixin
from app.models.persistence.hasher import HasherReferenceModel
from pynamodb.attributes import JSONAttribute, ListAttribute, MapAttribute, NumberAttribute, UnicodeAttribute, \
    UTCDateTimeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex


class KennelNameIndex(GlobalSecondaryIndex):
    class Meta(BaseMeta):
        index_name = 'kennel_name_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    lower_name = UnicodeAttribute(hash_key=True)


class KennelAcronymIndex(GlobalSecondaryIndex):
    class Meta(BaseMeta):
        index_name = 'kennel_acronym_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    lower_acronym = UnicodeAttribute(hash_key=True)
    lower_name = UnicodeAttribute(range_key=True)


# The Kennel Data model holds all non-list kennel data
# It includes a feature to automatically set the lower_name form of
# the kennel name, for case insensitve searching, but any update to the
#  kennel name requires that lower_name be automatically updated.
# This is a price to pay for using atomic updates.
class KennelDataModel(TimeStampableMixin, VersionMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'kennels'

    def __init__(self, hash_key=None, range_key=None, **attributes):
        meta_attributes = ['kennel_id']
        try:
            self.__meta_attributes__.extend(meta_attributes)
        except AttributeError:
            self.__meta_attributes__ = meta_attributes
        super().__init__(hash_key, range_key, **attributes)

    kennel_id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    lower_name = UnicodeAttribute()
    acronym = UnicodeAttribute()
    lower_acronym = UnicodeAttribute()
    region = ListAttribute(null=True)
    contact = JSONAttribute(null=True)
    webpage = UnicodeAttribute(null=True)
    facebook = UnicodeAttribute(null=True)
    founding = JSONAttribute(null=True)
    description = UnicodeAttribute(null=True)
    next_trail_number = NumberAttribute(null=True)
    name_index = KennelNameIndex()
    acronym_index = KennelAcronymIndex()

    def save(self, condition=None, conditional_operator=None, **expected_values):
        matches = self.matching_records_by_name(self)
        if matches:
            msg = f'Record with name {self.name} already exists.'
            raise AlreadyExists(msg)
        super().save(condition=condition, conditional_operator=conditional_operator, **expected_values)

    def to_ref(self):
        return KennelReferenceModel(kennel_id=self.kennel_id, name=self.name, acronym=self.acronym)

    @classmethod
    def matching_records(cls, record, filter_self=True):
        if record.lower_name is None:
            raise ValueError('Lower name cannot be None.')
        query_result = cls.name_index.query(record.lower_name)
        record_attrs = record.attributes()
        results = [result for result in query_result if cls._record_match(result.attributes(), record_attrs)]
        if filter_self:
            results = [result for result in results if result.kennel_id != record.kennel_id]
        return results

    @classmethod
    def matching_records_by_name(cls, record, filter_self=True):
        if record.lower_name is None:
            raise ValueError('Lower name cannot be None.')
        query_result = cls.name_index.query(record.lower_name)
        results = [result for result in query_result if result.lower_name == record.lower_name]
        if filter_self:
            results = [result for result in results if result.kennel_id != record.kennel_id]
        return results

    @classmethod
    def record_exists(cls, record):
        return cls.count(record.kennel_id) > 0

    @staticmethod
    def _record_match(a, b):
        try:
            return all([a[key] == b[key] for key in a.keys()])
        except KeyError:
            return False


class HasherMembershipIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'hasher_membership_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    hasher_id = UnicodeAttribute(hash_key=True)
    kennel_id = UnicodeAttribute(range_key=True)


class KennelReferenceModel(MapAttribute):
    kennel_id = UnicodeAttribute()
    name = UnicodeAttribute()
    acronym = UnicodeAttribute()

    def is_ref(self, kennel):
        if not isinstance(kennel, KennelDataModel):
            return False
        for attr in self.attribute_values.keys():
            if self.attribute_values[attr] != kennel.attribute_values[attr]:
                return False
        return True

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__


# The kennel member data model holds the list of hashers that are members of a given kennel
class KennelMemberDataModel(TimeStampableMixin, VersionMixin, BaseModel):
    class Meta(BaseMeta):
        table_name = 'kennel_members'

    kennel_id = UnicodeAttribute(hash_key=True)
    kennel_ref = KennelReferenceModel()
    hasher_id = UnicodeAttribute(range_key=True)
    hasher_ref = HasherReferenceModel()
    joined = UTCDateTimeAttribute(null=True)
    hasher_membership_index = HasherMembershipIndex()

    @classmethod
    def members(cls, kennel_id):
        return [result.hasher_ref for result in cls.query(kennel_id)]
