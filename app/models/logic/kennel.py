from ulid import ulid
from app.models.persistence.kennel import KennelDataModel


class KennelLogicModel(object):
    __unpersistable_attributes__ = ['events', 'members', 'officers', 'persistence_object']

    def __init__(self, name, acronym, kennel_id=None, description=None, region=None, contact=None, webpage=None,
                 founding=None, next_trail_number=None, facebook=None, lower_acronym=None, lower_name=None,
                 persistence_object=None):
        self.kennel_id = ulid() if kennel_id is None else kennel_id
        self.name = name
        self.lower_name = lower_name
        self.acronym = acronym
        self.lower_acronym = lower_acronym
        self.region = region
        self.events = None
        self.members = None
        self.officers = None
        self.contact = contact
        self.webpage = webpage
        self.facebook = facebook
        self.founding = founding
        self.description = description
        self.next_trail_number = next_trail_number
        if persistence_object is None:
            self.persistence_object = KennelDataModel(**self.persistable_attributes())
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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise(NotImplemented, f"Equality between {self.__class__} and {other.__class__} is not supported.")
        return self.persistable_attributes() == other.persistable_attributes()

    @classmethod
    def create(cls, name, acronym, kennel_id=None, description=None, region=None, contact=None, webpage=None,
               founding=None, next_trail_number=None, facebook=None, persistence_object=None):
        kennel = KennelLogicModel(name, acronym, kennel_id=kennel_id, description=description, region=region,
                                  contact=contact, webpage=webpage, founding=founding,
                                  next_trail_number=next_trail_number, facebook=facebook,
                                  persistence_object=persistence_object)
        kennel.save()
        return kennel

    @classmethod
    def exists(cls, id=None, name=None):
        if id is not None:
            return cls.exists_by_id(id)
        elif name is not None:
            return cls.exists_by_name(name)
        else:
            raise(ValueError, 'One of id or name must be provided to check for existence.')

    @classmethod
    def exists_by_id(cls, kennel_id):
        result = KennelDataModel.count(kennel_id)
        return result > 0

    @classmethod
    def exists_by_name(cls, kennel_name):
        result = KennelDataModel.name_index.count(kennel_name.lower())
        return result > 0

    @classmethod
    def lookup_by_id(cls, kennel_id):
        result = KennelDataModel.get(kennel_id)
        attribute_dict = result.attributes()
        attribute_dict['persistence_object'] = result
        return KennelLogicModel(**attribute_dict)
