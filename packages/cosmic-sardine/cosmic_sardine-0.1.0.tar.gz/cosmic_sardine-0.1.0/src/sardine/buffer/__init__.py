


class View:
    def __init__(self, pkg, mapper):
        self.pkg = pkg
        self.mapper = mapper

    @property
    def view(self):
        return self.mapper.from_memoryview(self.pkg.bytes)

    @view.setter
    def view(self, value):
        if isinstance(value, self.mapper.type):
            mv = self.mapper.as_memoryview(value)
            self.pkg.bytes[:] = mv
        else:
            raise TypeError(f"Value must be of type {self.mapper.type}")


class Producer:


    def __init__(self, pkg, mapper):
        self.pkg = pkg
        self.mapper = mapper
