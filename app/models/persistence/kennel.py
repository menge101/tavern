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

    searchable_name = UnicodeAttribute(hash_key=True)


class KennelAcronymIndex(GlobalSecondaryIndex):
    class Meta(BaseMeta):
        index_name = 'kennel_acronym_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    searchable_acronym = UnicodeAttribute(hash_key=True)
    searchable_name = UnicodeAttribute(range_key=True)


# The Kennel Data model holds all non-list kennel data
# It includes a feature to automatically set the lower_name form of
# the kennel name, for case insensitve searching, but any update to the
#  kennel name requires that lower_name be automatically updated.
# This is a price to pay for using atomic updates.
class KennelDataModel(TimeStampableMixin, VersionMixin, BaseModel):
    __before_save_hooks__ = ['set_searchable_name', 'set_searchable_acronym']
    __on_init_hooks__ = ['set_searchable_name', 'set_searchable_acronym']
    __update_action_hooks__ = {'set': {'name': 'set_searchable_name_action',
                                       'acronym': 'set_searchable_acronym_action'}}

    class Meta(BaseMeta):
        table_name = 'kennels'

    def __init__(self, hash_key=None, range_key=None, **attributes):
        meta_attributes = ['kennel_id', 'searchable_name', 'searchable_acronym']
        self.assign_or_extend('__meta_attributes__', meta_attributes)
        self.assign_or_extend('on_init_hooks', __class__.__on_init_hooks__)
        self.assign_or_extend('before_save_hooks', __class__.__before_save_hooks__)
        self.assign_or_update('update_action_hooks', __class__.__update_action_hooks__)
        super().__init__(hash_key, range_key, **attributes)

    kennel_id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    searchable_name = UnicodeAttribute()
    acronym = UnicodeAttribute()
    searchable_acronym = UnicodeAttribute()
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

    def set_searchable_acronym(self):
        if self.acronym is None:
            raise ValueError('acronym cannot be None')
        self.searchable_acronym = self.searchable_value(self.acronym)

    def set_searchable_acronym_action(self, acronym):
        return [KennelDataModel.searchable_acronym.set(self.searchable_value(acronym))]

    def set_searchable_name(self):
        if self.name is None:
            raise ValueError('name cannot be None')
        self.searchable_name = self.searchable_value(self.name)

    def set_searchable_name_action(self, name):
        return [KennelDataModel.searchable_name.set(self.searchable_value(name))]

    def to_ref(self):
        return KennelReferenceModel(kennel_id=self.kennel_id, name=self.name, acronym=self.acronym)

    @classmethod
    def matching_records(cls, record, filter_self=True):
        if record.searchable_name is None:
            raise ValueError('searchable name cannot be None.')
        query_result = cls.name_index.query(record.searchable_name)
        record_attrs = record.attributes()
        results = [result for result in query_result if cls._record_match(result.attributes(), record_attrs)]
        if filter_self:
            results = [result for result in results if result.kennel_id != record.kennel_id]
        return results

    @classmethod
    def matching_records_by_name(cls, record, filter_self=True):
        if record.searchable_name is None:
            raise ValueError('searchable name cannot be None.')
        query_result = cls.name_index.query(record.searchable_name)
        results = [result for result in query_result if result.searchable_name == record.searchable_name]
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
