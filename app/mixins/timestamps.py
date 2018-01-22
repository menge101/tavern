from datetime import datetime, timezone
from pynamodb.attributes import UTCDateTimeAttribute
from pynamodb.models import Model


# This mixin adds two change tracking fields to the object and also adds a
# save hook to set those values on every create and edit.  THe save hook
# functionality only works with a save designed to
class TimeStampableMixin(Model):
    created_at = UTCDateTimeAttribute()
    modified_at = UTCDateTimeAttribute()

    def generate_timestamp_update_action(self):
        return self.__class__.modified_at.set(datetime.now(timezone.utc))

    def set_timestamps(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        self.modified_at = datetime.now(timezone.utc)

    # the following code assumes that the __save_before_hooks__ attribute already
    #  exists and attempts to append to it.  It will except on a NameError,
    # meaning that the attribute does not exist, and it will create it.
    try:
        __before_save_hooks__.append('set_timestamps')
    except NameError:
        __before_save_hooks__ = ['set_timestamps']

    try:
        __on_update_hooks__.append('generate_timestamp_update_action')
    except NameError:
        __on_update_hooks__ = ['generate_timestamp_update_action']
