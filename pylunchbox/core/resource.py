import inspect
import os

class ResourceManager(object):
    
    def __init__(self):

        # Retrieve the path that this source file is in
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        this_path = os.path.dirname(os.path.abspath(filename))
        path_parts = this_path.split("\\")
        while path_parts[-1] != "pylunchbox":
            path_parts.pop()
        path_parts.append("res")
        self._path = "/".join(path_parts)

    def get_path(self):
        """ Get the current path that the core is in. """

        return self._path

    path = property(get_path, doc=get_path.__doc__)

if __name__ == "__main__":

    rm = ResourceManager()
    print rm.path