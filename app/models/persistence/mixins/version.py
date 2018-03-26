from app.models.persistence.base import BaseModel
from pynamodb.attributes import NumberAttribute


# This mixin adds the ability to create and maintain an incrementing version
class VersionMixin(BaseModel):
    version = NumberAttribute()
    __before_save_hooks__ = ['set_version']
    __on_update_hooks__ = ['generate_version_update_action']

    def __init__(self, hash_key=None, range_key=None, **attributes):
        self.assign_or_extend('before_save_hooks', __class__.__before_save_hooks__)
        self.assign_or_extend('on_update_hooks', __class__.__on_update_hooks__)
        self.assign_or_extend('__meta_attributes__', ['version'])
        super().__init__(hash_key, range_key, **attributes)

    def generate_version_update_action(self):
        next_version = 0 if self.version is None else self.version + 1
        return self.__class__.version.set(next_version)

    def set_version(self):
        self.version = 0
