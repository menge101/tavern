from .event_tests import EventTests
from .hasher_tests import HasherTests
from .kennel_tests import KennelTests

__all__ = ['EventTests', 'HasherTests', 'KennelTests']

# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)
