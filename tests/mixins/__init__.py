from .multi_mixin_tests import MultiMixinTests
from .timestamp_tests import TimestampTests
from .version_tests import VersionTests

# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)

__all__ = ['MultiMixinTests', 'TimestampTests', 'VersionTests']
