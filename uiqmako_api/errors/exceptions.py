
class UIQMakoBaseException(Exception):

    def __init__(self, msg):
        super(UIQMakoBaseException, self).__init__()
        self.msg = msg

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.__repr__()


class UsernameExists(UIQMakoBaseException):
    def __init__(self):
        super().__init__(
            msg="Username already in use"
        )


class XmlIdNotFound(UIQMakoBaseException):
    def __init__(self, msg):
        super().__init__(
            msg=msg)


class InvalidId(UIQMakoBaseException):
    def __init__(self, msg):
        super().__init__(
            msg=msg)
