from .event_tests import EventTableTests, EventTests
from .hasher_tests import HasherTests
from .kennel_tests import KennelTests

__all__ = ['EventTests', 'EventTableTests', 'HasherTests', 'KennelTests']

# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)
