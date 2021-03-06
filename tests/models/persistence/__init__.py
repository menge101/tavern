from tests.models.persistence.base_tests import BaseTests
from tests.models.persistence.event_tests import EventTests
from tests.models.persistence.hasher_tests import HasherTests
from tests.models.persistence.kennel_tests import KennelTests
from tests.models.persistence.kennel_member_tests import KennelMemberTests

__all__ = ['BaseTests', 'EventTests', 'HasherTests', 'KennelTests', 'KennelMemberTests']

# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)
