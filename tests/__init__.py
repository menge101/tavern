from .mixins import MultiMixinTests, TimestampTests, VersionTests
from .models import EventTests, HasherTests, KennelTests
from .pynamo_tests import PynamoTests
# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)

__all__ = ['EventTests', 'HasherTests', 'KennelTests', 'MultiMixinTests', 'PynamoTests',
           'TimestampTests', 'VersionTests']
