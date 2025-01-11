from abc import ABCMeta, abstractmethod


class MongoRepository(metaclass=ABCMeta):
    @abstractmethod
    def is_up(self, log) -> bool:
        raise NotImplementedError
    
    
    @abstractmethod
    def config_general(self, log, *args, **kwargs) -> dict:
        raise NotImplementedError