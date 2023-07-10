class FileID:
    def __init__(self, origin, identifier):
        self.__origin = origin
        self.__identifier = identifier

    @classmethod
    def from_local_path(cls, path):
        if not isinstance(path, str):
            path = str(path)

        return cls("local", path)

    @classmethod
    def from_internal_id(cls, identifier, resource="project"):
        return cls(resource, identifier)
