from ulid import ulid
from app.models.persistence import AlreadyExists
from app.models.persistence.kennel import KennelDataModel, KennelMemberDataModel
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
        self.members = list()
        self.officers = None
        self.contact = contact
        self.webpage = webpage
        self.facebook = facebook
        self.founding = founding
        self.description = description
        self.next_trail_number = next_trail_number
        self.load_members()
        if persistence_object is None:
            self.persistence_object = KennelDataModel(**self.persistable_attributes())
        else:
            self.persistence_object = persistence_object

    def add_member(self, hasher_id):
        if self.has_member(hasher_id):
            raise AlreadyExists(f'{self.name} already has a member with id {hasher_id}')
        self.create_membership(self.kennel_id, hasher_id)
        self.load_members()

    def has_member(self, hasher_id):
        return hasher_id in self.members

    def load_members(self):
        self.members = self.list_members(self.kennel_id)

    @staticmethod
    def _extract_hasher_ids_from_query(result):
        result = list(result)
        if len(result) == 0:
            return list()
        return [member_record.attributes()['hasher_id'] for member_record in result]

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
    def create_membership(kennel_id, hasher_id):
        KennelMemberDataModel(kennel_id, hasher_id).save()

    @staticmethod
    def lookup_by_id(kennel_id):
        result = KennelDataModel.get(kennel_id)
        attribute_dict = result.attributes()
        attribute_dict['persistence_object'] = result
        attribute_dict['kennel_id'] = kennel_id
        return KennelLogicModel(**attribute_dict)

    @classmethod
    def list_members(cls, kennel_id):
        raw_result = KennelMemberDataModel.query(kennel_id)
        return cls._extract_hasher_ids_from_query(raw_result)

