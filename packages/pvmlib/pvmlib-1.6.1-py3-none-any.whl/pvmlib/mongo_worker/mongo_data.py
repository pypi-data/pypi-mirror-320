from pvmlib.database import Database, Session
from pymongo import MongoClient, errors
from contextlib import contextmanager, suppress
from collections.abc import Iterator
from pvmlib.utils import Utils

class MongoSession(Session):
    def __init__(self, db_uri: str, database: str, timeout: int, max_pool_size: int) -> None:
        self.__client = MongoClient(
            db_uri, 
            serverSelectionTimeoutMS=timeout,
            maxPoolSize=max_pool_size
        )
        self.__db_appcom = self.__client[database]

    def __enter__(self): 
        return self

    def db_appcom(self):
        return self.__db_appcom

    def is_up(self) -> dict:
        data = {
            "status": True,
            "message": "Success",
            "method": Utils.get_method_name(self, "is_up")
        }

        try:
            self.__client.server_info()
            self.__client.admin.command("ping")
        except errors.PyMongoError as ex:
            data["status"] = False
            data["message"] = str(ex)
        
        return data

    def __exit__(self, exception_type, exception_value, traceback) -> None: 
        self.__client.close()


class MongoDatabase(Database):
    def __init__(self, db_uri: str, database: str, timeout: int, max_pool_size: int) -> None:
        self.__session = MongoSession(
            db_uri,
            database,
            timeout,
            max_pool_size
        )

    @contextmanager
    def session(self) -> Iterator[Session]:
        with suppress(Exception):
            yield self.__session