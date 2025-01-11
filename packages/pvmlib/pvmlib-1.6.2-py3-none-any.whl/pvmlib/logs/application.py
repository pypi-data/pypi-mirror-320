class Application(object):

    def __init__(self, name: str, version: str, env: str, kind: str) -> None:
        self.name = name
        self.version = version
        self.env = env
        self.kind = kind

    def get_info_application(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "env": self.env,
            "kind": self.kind
        }