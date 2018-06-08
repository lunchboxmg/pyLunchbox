import inspect
import os
import imageio

filename = inspect.getframeinfo(inspect.currentframe()).filename
this_path = os.path.dirname(os.path.abspath(filename))
path_parts = this_path.split("\\")
while path_parts[-1] != "pylunchbox":
    path_parts.pop()
path = "/".join(path_parts)
print path


filename = path + "/res/fonts/consolas_asc.png"

img = imageio.imread(filename)

print img.shape