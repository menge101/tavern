from ulid import ulid
from app.models.logic.base import LogicBase
from app.models.persistence.hasher import HasherDataModel


class HasherLogicModel(LogicBase):
    def __init__(self, hash_name, mother_kennel, hasher_id=None, contact_info=None, real_name=None, user=None,
                 persistence_object=None):
        super().__init__()
        self.hasher_id = ulid() if hasher_id is None else hasher_id
        self.hash_name = hash_name
        if hasattr(mother_kennel, 'create'):
            self.mother_kennel = self.map_mother_kennel(mother_kennel)
        else:
            self.mother_kennel = mother_kennel
        self.contact_info = contact_info
        self.real_name = real_name
        self.user = user
        if persistence_object is None:
            self.persistence_object = HasherDataModel(**self.persistable_attributes())
        else:
            self.persistence_object = persistence_object

    @classmethod
    def create(cls, hash_name, mother_kennel, hasher_id=None, contact_info=None, real_name=None, user=None,
               persistence_object=None):
        hasher = HasherLogicModel(hash_name, mother_kennel, hasher_id=hasher_id, contact_info=contact_info,
                                  real_name=real_name, user=user, persistence_object=persistence_object)
        hasher.save()
        return hasher

    @classmethod
    def lookup_by_id(cls, hasher_id):
        result = HasherDataModel.get(hasher_id)
        attribute_dict = result.attributes()
        attribute_dict['persistence_object'] = result
        attribute_dict['hasher_id'] = result.hasher_id
        return HasherLogicModel(**attribute_dict)

    @staticmethod
    def map_mother_kennel(momma):
        return {'kennel_id': momma.kennel_id, 'name': momma.name, 'acronym': momma.acronym}
