from .logs import Measurement
import time


class Cache(object):

    get_time_elapsed_ms = lambda self, init_time=None, decimals=2: round((time.perf_counter()-init_time)*1000, decimals)
    cached_responses = {}

    def __call__(self, func):
        def get_config_cached(*args, **kwargs):
            full_name = func.__qualname__
            log = kwargs.get("log")
            update_cache = kwargs.get("update_cache")
            is_cached = self.cached_responses.get(full_name) != None
            if is_cached:
                is_cached = self.cached_responses.get(full_name)["data"] != None
            if not is_cached or update_cache:
                res = func(*args, **kwargs)
                self.cached_responses[full_name] = {"data": res}
            elif log: 
                init_time = time.perf_counter()
                measurement = Measurement("MongoDB", self.get_time_elapsed_ms(init_time))
                log.info(f"Get cache data from MongoDB: {full_name}", measurement=measurement)
            return self.cached_responses[full_name]["data"]
        return get_config_cached
    
    @classmethod
    def get_cached_response(cls, func_name: str) -> dict:
        return cls.cached_responses.get(func_name)