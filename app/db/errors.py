"""
DBError
    +-- EntityDoesNotExistError
"""


class DBError(Exception):
    """ Common DB exception. """


class EntityDoesNotExistError(DBError):
    """ Raised if the searched entity does not exist in the database. """
