from .common import clean_create_tables
from .kennel import KennelLogicTests, KennelMembershipTests

__all__ = ['KennelLogicTests', 'KennelMembershipTests', 'clean_create_tables']

# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)
