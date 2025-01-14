import logging
from typing import Optional

from aporacle.data.db.crud import Crud

from flareprovider.logger import FlareProviderLogger


class MongoConnectionManager(Crud):
    _logger: Optional[FlareProviderLogger] = None
    _mongo_instance: Optional["MongoConnectionManager"] = None

    @classmethod
    def logger(cls) -> FlareProviderLogger:
        if cls._logger is None:
            cls._logger = logging.getLogger(__name__)
        return cls._logger

    def __init__(self, uri: str, db_name: str):
        super().__init__(uri, db_name)
