from .kennel import KennelLogicTests, KennelMembershipTests

__all__ = ['KennelLogicTests', 'KennelMembershipTests']

# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)
