from ulid import ulid
from app.models.persistence.hasher import HasherDataModel


class HasherLogicModel(object):
    __unpersistable_attributes__ = ['persistence_object']

    def __init__(self, hash_name, mother_kennel, hasher_id=None, contact_info=None, real_name=None, user=None,
                 lower_hash_name=None, persistence_object=None):
        self.hasher_id = ulid() if hasher_id is None else hasher_id
        self.hash_name = hash_name
        self.lower_hash_name = lower_hash_name
        self.mother_kennel = mother_kennel
        self.contact_info = contact_info
        self.real_name = real_name
        self.user = user
        if persistence_object is None:
            self.persistence_object = HasherDataModel(**self.persistable_attributes())
        else:
            self.persistence_object = persistence_object

    def persistable_attributes(self):
        return {k: v for (k, v) in self.__dict__.items() if k not in self.__unpersistable_attributes__}

    def reload_from_persistence(self):
        for (k, v) in self.persistence_object.attributes().items():
            if hasattr(self, k):
                setattr(self, k, v)

    def save(self):
        self.persistence_object.save()
        self.reload_from_persistence()
        return self

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise(NotImplemented, f"Equality between {self.__class__} and {other.__class__} is not supported.")
        return self.persistable_attributes() == other.persistable_attributes()

    @classmethod
    def create(cls, hash_name, mother_kennel, hasher_id=None, contact_info=None, real_name=None, user=None,
               lower_hash_name=None, persistence_object=None):
        hasher = HasherLogicModel(hash_name, mother_kennel, hasher_id=hasher_id, contact_info=contact_info,
                                  real_name=real_name, user=user, lower_hash_name=lower_hash_name,
                                  persistence_object=persistence_object)
        hasher.save()
        return hasher

    @classmethod
    def exists(cls, id=None, hash_name=None):
        if id is not None:
            return cls.exists_by_id(id)
        elif hash_name is not None:
            return cls.exists_by_hash_name(hash_name)
        else:
            raise (ValueError, 'One of id or hash_name must be provided to check for existence.')

    @classmethod
    def exists_by_id(cls, hasher_id):
        result = HasherDataModel.count(hasher_id)
        return result > 0

    @classmethod
    def exists_by_hash_name(cls, hash_name):
        result = HasherDataModel.hash_name_index.count(hash_name.lower())
        return result > 0

    @classmethod
    def lookup_by_id(cls, hasher_id):
        result = HasherDataModel.get(hasher_id)
        attribute_dict = result.attributes()
        attribute_dict['persistence_object'] = result
        return HasherLogicModel(**attribute_dict)
