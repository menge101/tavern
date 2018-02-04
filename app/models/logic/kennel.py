from ulid import ulid
from app.models.persistence.kennel import KennelDataModel
from app.models.logic.base import LogicBase


class KennelLogicModel(LogicBase):
    __unpersistable_attributes__ = ['events', 'members', 'officers']

    def __init__(self, name, acronym, kennel_id=None, description=None, region=None, contact=None, webpage=None,
                 founding=None, next_trail_number=None, facebook=None, lower_acronym=None, lower_name=None,
                 persistence_object=None):
        if lower_acronym is None:
            lower_acronym = acronym.lower()
        if lower_name is None:
            lower_name = name.lower()
        super().__init__()
        self.unpersist_values(__class__)
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

    @classmethod
    def create(cls, name, acronym, kennel_id=None, description=None, region=None, contact=None, webpage=None,
               founding=None, next_trail_number=None, facebook=None, persistence_object=None):
        kennel = KennelLogicModel(name, acronym, kennel_id=kennel_id, description=description, region=region,
                                  contact=contact, webpage=webpage, founding=founding,
                                  next_trail_number=next_trail_number, facebook=facebook,
                                  persistence_object=persistence_object)
        kennel.save()
        return kennel

    @staticmethod
    def lookup_by_id(kennel_id):
        result = KennelDataModel.get(kennel_id)
        attribute_dict = result.attributes()
        attribute_dict['persistence_object'] = result
        attribute_dict['kennel_id'] = kennel_id
        return KennelLogicModel(**attribute_dict)
