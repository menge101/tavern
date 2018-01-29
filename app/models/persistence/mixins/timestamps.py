from copy import copy
from datetime import datetime, timezone
from pynamodb.attributes import UTCDateTimeAttribute
from pynamodb.models import Model


# This mixin adds two change tracking fields to the object and also adds a
# save hook to set those values on every create and edit.  THe save hook
# functionality only works with a save designed to
class TimeStampableMixin(Model):
    created_at = UTCDateTimeAttribute()
    modified_at = UTCDateTimeAttribute()
    __before_save_hooks__ = ['set_timestamps']
    __on_update_hooks__ = ['generate_timestamp_update_action']

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

        meta_attributes = ['created_at', 'modified_at']
        try:
            self.__meta_attributes__.extend(meta_attributes)
        except AttributeError:
            self.__meta_attributes__ = meta_attributes

        super().__init__(hash_key, range_key, **attributes)

    def generate_timestamp_update_action(self):
        return self.__class__.modified_at.set(datetime.now(timezone.utc))

    def set_timestamps(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        self.modified_at = datetime.now(timezone.utc)
