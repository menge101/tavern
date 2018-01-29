from tests.models.persistence import EventTests, HasherTests, KennelTests

__all__ = ['EventTests', 'HasherTests', 'KennelTests']

# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)
