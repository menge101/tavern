from pynamodb.attributes import ListAttribute, UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model


class PynamoTestModel(Model):
    class Meta:
        table_name = 'pynamo_tests'

    test_id = UnicodeAttribute(hash_key=True)
    list = ListAttribute()
    description = UnicodeAttribute()
    start_time = UTCDateTimeAttribute()
    end_time = UTCDateTimeAttribute(null=True)
