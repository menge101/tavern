import os
from pynamodb.models import Model


class BaseMeta(object):
    host = os.environ.get('DYNAMODBURL')


class BaseModel(Model):
    def __init__(self, hash_key=None, range_key=None, **attributes):
        super(BaseModel, self).__init__(hash_key, range_key, **attributes)

    def attributes(self):
        return {k: v for (k, v) in self.attribute_values.items() if k not in self.__meta_attributes__}

    def save(self, condition=None, conditional_operator=None, **expected_values):
        for hook in self.before_save_hooks:
            getattr(self, hook)()
        super(BaseModel, self).save(condition=condition, conditional_operator=conditional_operator, **expected_values)

    def update(self, attributes=None, actions=None, condition=None, conditional_operator=None, **expected_values):
        actions.extend([getattr(self, hook)() for hook in self.on_update_hooks])
        super(BaseModel, self).update(attributes=attributes, actions=actions, condition=condition,
                                      conditional_operator=conditional_operator, **expected_values)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
