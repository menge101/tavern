from ulid import ulid

from app.models.persistence.kennel import KennelDataModel


class KennelLogicModel(object):
    def __init__(self, name, acronym, kennel_id=None, description=None, region=None, contact=None, webpage=None,
                 founding=None, next_trail_number=None, facebook=None, persistence_object=None):
        self.kennel_id = ulid() if kennel_id is None else kennel_id
        self.name = name
        self.acronym = acronym
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
            self.persistence_object = KennelDataModel(self.__dict__)

    @classmethod
    def lookup(cls, kennel_id):
        result = KennelDataModel.get(kennel_id)
        attribute_dict = result.attributes()
        attribute_dict['persistence_object'] = result
        return KennelLogicModel(**attribute_dict)

