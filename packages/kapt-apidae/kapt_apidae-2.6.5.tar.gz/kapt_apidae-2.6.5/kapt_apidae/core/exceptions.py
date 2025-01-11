class ObjectUnchangedException(Exception):
    """The object hasn't changed since the last import"""

    pass


class ObjectUpdateFailedException(Exception):
    """An error occured while trying to update object"""

    pass
