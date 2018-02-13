from copy import copy


class LogicBase(object):
    __unpersistable_attributes__ = ['persistence_object', '_unpersistable_attributes_']

    def __init__(self):
        self._unpersistable_attributes_ = list()
        self.unpersist_values(__class__)
        self.persistence_object = None

    def persistable_attributes(self):
        return {k: v for (k, v) in self.__dict__.items() if k not in self._unpersistable_attributes_}

    def reload_from_persistence(self):
        if self.persistence_object is None:
            raise ValueError('Persistence object not successfully created or set.')
        for (k, v) in self.persistence_object.attributes().items():
            if hasattr(self, k):
                setattr(self, k, v)

    def save(self):
        self.persistence_object.save()
        self.reload_from_persistence()

    def unpersist_values(self, klazz):
        values = copy(klazz.__unpersistable_attributes__)
        try:
            self._unpersistable_attributes_.extend(values)
        except AttributeError:
            self._unpersistable_attributes_ = values

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError(f"Equality between {self.__class__} and {other.__class__} is not supported.")
        return self.persistable_attributes() == other.persistable_attributes()
