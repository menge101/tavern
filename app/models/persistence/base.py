from copy import copy
import functools
import os
import re
from pynamodb.models import Model


class BaseMeta(object):
    host = os.environ.get('DYNAMODBURL')


class BaseModel(Model):
    VALID_UPDATE_ACTIONS = ['set', 'remove', 'add', 'delete']
    __before_save_hooks__ = list()
    __on_init_hooks__ = list()
    __update_hooks__ = list()
    __update_action_hooks__ = dict()

    def __init__(self, hash_key=None, range_key=None, **attributes):
        self.assign_or_extend('before_save_hooks', __class__.__before_save_hooks__)
        self.assign_or_extend('on_init_hooks', __class__.__on_init_hooks__)
        self.assign_or_extend('on_update_hooks', __class__.__update_hooks__)
        self.assign_or_update('update_action_hooks', __class__.__update_action_hooks__)
        super(BaseModel, self).__init__(hash_key, range_key, **attributes)
        self.update_actions = list()
        for hook in self.on_init_hooks:
            getattr(self, hook)()

    def add_update_action(self, field, action, value=None):
        action = action.lower()
        if action not in self.VALID_UPDATE_ACTIONS:
            raise ValueError(f"Actions {action} is not one of {', '.join(self.VALID_UPDATE_ACTIONS)}")
        field_obj = self.__get_field_object__(field)
        if field_obj.is_hash_key or field_obj.is_range_key:
            raise ValueError(f"Field cannot be used because it is part of the key.")
        action_obj = getattr(field_obj, action)
        if value:
            thing = action_obj(value)
        else:
            thing = action_obj()
        self.update_actions.append(thing)
        if self.update_action_hooks.get(action, {field: None}).get(field):
            self.update_actions.extend(getattr(self, self.update_action_hooks[action][field])(value))

    @classmethod
    def __get_field_object__(cls, field):
        return functools.reduce(lambda x, y: getattr(x, y), field.split('.'), cls)

    def assign_or_extend(self, field, value_list):
        copied_list = copy(value_list)
        if not hasattr(value_list, 'extend'):
            raise ValueError(f'{self.__class__}#assign_or_extend expects a list-like object for the value_list')
        try:
            self.__getattribute__(field).extend(copied_list)
        except AttributeError:
            self.__setattr__(field, copied_list)

    def assign_or_update(self, field, value_dict):
        copied_dict = copy(value_dict)
        if not hasattr(value_dict, 'update'):
            raise ValueError(f'{self.__class__}#assign_or_update expects a dict-like object for the value_list')
        try:
            self.__getattribute__(field).update(copied_dict)
        except AttributeError:
            self.__setattr__(field, copied_dict)

    def attributes(self):
        return {k: v for (k, v) in self.attribute_values.items() if k not in self.__meta_attributes__}

    def clear_update_set(self):
        self.update_actions = list()

    def save(self, condition=None, conditional_operator=None, **expected_values):
        for hook in self.before_save_hooks:
            getattr(self, hook)()
        super(BaseModel, self).save(condition=condition, conditional_operator=conditional_operator, **expected_values)

    def to_ref(self, reference_class):
        valid_keys = [key for key in reference_class.__dict__.keys() if not key.startswith('_')]
        return reference_class(**{k: v for k, v in self.attributes().items() if k in valid_keys})

    def update(self, attributes=None, condition=None, conditional_operator=None, **expected_values):
        if self.update_actions is None:
            raise ValueError('Update Action list is empty. (Use #add_update_action to create update actions')
        actions = self.update_actions
        self.update_actions = list()
        actions.extend([getattr(self, hook)() for hook in self.on_update_hooks])
        super(BaseModel, self).update(attributes=attributes, actions=actions, condition=condition,
                                      conditional_operator=conditional_operator, **expected_values)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.attributes() == other.attributes()

    # This method exists to create consistent searchable names.  If a hasher exists with a name
    # of 'Cheesy Grits', we can be reasonably sure that 'Cheesy  Grits', 'cheesy grits', 'Cheesy grits'
    # can not also is not also get created
    @staticmethod
    def searchable_value(value):
        return re.sub(r'\s+', '', value).lower()
