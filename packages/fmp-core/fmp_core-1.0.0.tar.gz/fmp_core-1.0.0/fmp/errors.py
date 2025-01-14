"""
Module for custom exceptions.

"""

import logging
from abc import ABCMeta


class BaseMessageException(Exception, metaclass=ABCMeta):
    """Base exception class for displaying messages."""

    __message = None

    def __init__(self, message: str = None, logger: logging.Logger = None) -> None:
        self.message = message or self.__message

        if logger:
            logger.error(self.message)


class NoDataException(BaseMessageException): ...


class NoProxyLoadedException(BaseMessageException): ...
