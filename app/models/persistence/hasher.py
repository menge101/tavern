from app.models.persistence.base import BaseModel
from app.models.persistence.mixins.timestamps import TimeStampableMixin
from pynamodb.attributes import JSONAttribute, UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, KeysOnlyProjection


class HashNameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'hash_name_index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()

    lower_hash_name = UnicodeAttribute(hash_key=True)
    mother_kennel = UnicodeAttribute(range_key=True)


class HasherDataModel(TimeStampableMixin, BaseModel):
    class Meta:
        table_name = 'hashers'

    def __init__(self, hash_key=None, range_key=None, **attributes):
        hook = ['set_searchable_hash_name']
        try:
            self.before_save_hooks.extend(hook)
        except AttributeError:
            self.before_save_hooks = hook
        super().__init__(hash_key, range_key, **attributes)

    hasher_id = UnicodeAttribute(hash_key=True)
    contact_info = JSONAttribute(null=True)
    hash_name = UnicodeAttribute()
    lower_hash_name = UnicodeAttribute()
    mother_kennel = UnicodeAttribute()
    real_name = UnicodeAttribute(null=True)
    user = UnicodeAttribute(null=True)
    hash_name_index = HashNameIndex()

    def set_searchable_hash_name(self):
        try:
            if self.lower_hash_name is None:
                self.lower_hash_name = self.hash_name.lower()
        except AttributeError:
            raise(ValueError('Value of hash_name cannot be None'))
