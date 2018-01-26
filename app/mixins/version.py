from pynamodb.attributes import NumberAttribute
from pynamodb.models import Model


# This mixin adds the ability to create and maintain a version identity
# based on the md5 hash of the object's state
class VersionMixin(Model):
    version = NumberAttribute()

    def generate_version_update_action(self):
        return self.__class__.version.set(self.version + 1)

    def set_version(self):
        self.version = 0

    # the following code assumes that the __save_before_hooks__ attribute already
    #  exists and attempts to append to it.  It will except on a NameError,
    # meaning that the attribute does not exist, and it will create it.
    try:
        __before_save_hooks__.append('set_version')
    except NameError:
        __before_save_hooks__ = ['set_version']

    try:
        __on_update_hooks__.append('generate_version_update_action')
    except NameError:
        __on_update_hooks__ = ['generate_version_update_action']
