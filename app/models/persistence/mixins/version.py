from copy import copy
from pynamodb.attributes import NumberAttribute
from pynamodb.models import Model


# This mixin adds the ability to create and maintain a version identity
# based on the md5 hash of the object's state
class VersionMixin(Model):
    version = NumberAttribute()
    __before_save_hooks__ = ['set_version']
    __on_update_hooks__ = ['generate_version_update_action']

    def __init__(self, hash_key=None, range_key=None, **attributes):
        before_hooks = copy(__class__.__before_save_hooks__)
        try:
            self.before_save_hooks.extend(before_hooks)
        except AttributeError:
            self.before_save_hooks = before_hooks

        update_hooks = copy(__class__.__on_update_hooks__)
        try:
            self.on_update_hooks.extend(update_hooks)
        except AttributeError:
            self.on_update_hooks = update_hooks

        meta_attributes = ['version']
        try:
            self.__meta_attributes__.extend(meta_attributes)
        except AttributeError:
            self.__meta_attributes__ = meta_attributes

        super().__init__(hash_key, range_key, **attributes)

    def generate_version_update_action(self):
        return self.__class__.version.set(self.version + 1)

    def set_version(self):
        self.version = 0
