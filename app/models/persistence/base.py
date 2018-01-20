from pynamodb.models import Model


class BaseModel(Model):
    def host(self, value=None):
        if value is not None:
            self.Meta.host = value
        return self.Meta.host

    def __eq__(self, other):
        return self.eq_dict(self.__dict__, other.__dict__)

    @classmethod
    def eq_dict(cls, a, b):
        if len(a) != len(b):
            return False
        a_keys = list(a.keys())
        b_keys = list(b.keys())
        a_keys.sort()
        b_keys.sort()
        if a_keys != b_keys:
            return False
        for key in a_keys:
            a_value = a[key]
            b_value = b[key]
            if hasattr(a_value, 'keys'):
                result = cls.eq_dict(a_value, b_value)
            elif hasattr(a_value, 'sort'):
                try:
                    a_value.sort()
                    b_value.sort()
                except TypeError:
                    pass
                result = a_value == b_value
            else:
                result = a_value == b_value
            if result is False:
                return False
        return True
