from app.models.persistence.base import BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from app.models.persistence.mixins.version import VersionMixin
from pynamodb.attributes import JSONAttribute, ListAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, KeysOnlyProjection


class KennelNameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'kennel_name_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()

    lower_name = UnicodeAttribute(hash_key=True)


class KennelAcronymIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'kennel_acronym_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()

    lower_acronym = UnicodeAttribute(hash_key=True)
    lower_name = UnicodeAttribute(range_key=True)


# The Kennel Data model holds all non-list kennel data
# It includes a feature to automatically set the lower_name form of
# the kennel name, for case insensitve searching, but any update to the
#  kennel name requires that lower_name be automatically updated.
# This is a price to pay for using atomic updates.
class KennelDataModel(TimeStampableMixin, VersionMixin, BaseModel):
    class Meta:
        table_name = 'kennels'

    def __init__(self, hash_key=None, range_key=None, **attributes):
        hook = ['set_search_values']
        try:
            self.before_save_hooks.extend(hook)
        except AttributeError:
            self.before_save_hooks = hook
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

    def set_search_values(self):
        try:
            if self.lower_acronym is None:
                self.lower_acronym = self.acronym.lower()
        except AttributeError:
            raise(ValueError('Value of acronym cannot be None'))
        try:
            if self.lower_name is None:
                self.lower_name = self.name.lower()
        except AttributeError:
            raise(ValueError('Value of name cannot be None'))
