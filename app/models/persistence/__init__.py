# https://www.python.org/dev/peps/pep-0382/
__import__('pkg_resources').declare_namespace(__name__)


# This exception is for all persistence module classes to use when needing to alert a calling functin that a record
# cannot be created due to a record already existing.
class AlreadyExists(BaseException):
    pass
