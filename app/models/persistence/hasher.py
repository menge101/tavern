from pynamodb.attributes import JSONAttribute, UnicodeAttribute
from app.models.persistence.base import BaseModel


class HasherDataModel(BaseModel):
    class Meta:
        table_name = 'hashers'

    hasher_id = UnicodeAttribute(hash_key=True)
    contact_info = JSONAttribute(null=True)
    hash_name = UnicodeAttribute()
    mother_kennel = UnicodeAttribute()
    real_name = UnicodeAttribute(null=True)
    user = UnicodeAttribute(null=True)

