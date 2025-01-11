class Utils:
    @staticmethod
    def get_method_name(obj, func_name: str = '') -> str:
        obj_class_name = f"{obj.__class__.__module__}.{obj.__class__.__qualname__}"
        full_name = obj_class_name + '.' + func_name if func_name else obj_class_name
        return full_name
    

    @staticmethod
    def add_attributes(obj, data: dict) -> None:
        for key, value in data.items():
            setattr(obj, key, value)
    

    @staticmethod
    def discard_empty_attributes(obj) -> None:
        obj_copy = obj.__dict__.copy()
        for key, value in obj_copy.items():
            if not value:
                delattr(obj, key)
    

    @staticmethod
    def sort_attributes(obj) -> None:
        obj.__dict__ = dict(sorted(obj.__dict__.items()))

    
    @staticmethod
    def get_error_data(error_details: dict, error_code: str) -> dict:
        return {
            "message": error_details[error_code]["message"],
            "status_code": int(error_details[error_code]["code_name"].split(".")[0]),
            "code_name": error_details[error_code]["code_name"]
        }
    

    @staticmethod
    def get_error_details(errors: dict) -> list:
        return list(map(lambda error: f"{error['loc'][1]}: {error['msg']} in {error['loc'][0]}", errors))
    

    @staticmethod
    def get_error_details_query_params(errors: dict) -> list:
        details = list(map(lambda error: f"{error['loc'][0]}: {error['msg']} in {error['loc'][1]}", errors))
        if "__root__" in details[0]:
            detail = details[0].replace("__root__", "puntodeventa")
            details[0] = detail
        return details
