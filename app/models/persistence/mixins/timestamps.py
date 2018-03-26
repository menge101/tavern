from app.models.persistence.base import BaseModel
from datetime import datetime, timezone
from pynamodb.attributes import UTCDateTimeAttribute


# This mixin adds two change tracking fields to the object and also adds a
# save hook to set those values on every create and edit.  THe save hook
# functionality only works with a save designed to
class TimeStampableMixin(BaseModel):
    created_at = UTCDateTimeAttribute()
    modified_at = UTCDateTimeAttribute()
    __before_save_hooks__ = ['set_timestamps']
    __on_update_hooks__ = ['generate_timestamp_update_action']

    def __init__(self, hash_key=None, range_key=None, **attributes):
        self.assign_or_extend('before_save_hooks', __class__.__before_save_hooks__)
        self.assign_or_extend('on_update_hooks', __class__.__on_update_hooks__)
        self.assign_or_extend('__meta_attributes__', ['created_at', 'modified_at'])
        super().__init__(hash_key, range_key, **attributes)

    @classmethod
    def generate_timestamp_update_action(cls):
        return cls.modified_at.set(datetime.now(timezone.utc))

    def set_timestamps(self):
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        self.modified_at = now
