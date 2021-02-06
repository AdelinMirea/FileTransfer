import os


class File(object):

    def __init__(self, name, path, size, type):
        self.name = name
        self.path = path
        self.size = size
        self.type = type

    def __str__(self):
        return "Name: {}\nPath: {}\nSize: {}\nType: {}\n".format(self.name,
                                                                 self.path,
                                                                 self.size,
                                                                 self.type)


def get_files(path=None, depth=0):
    if os.name == "nt":
        return _get_files_windows(path, depth)


def _get_files_windows(path=None, depth=0):
    if path is None:
        path = ["D:\\"]  # _get_drivers()
    else:
        path = [path]

    files = list()
    try:
        for dir in path:
            os.chdir(dir)
            _get_files_from_directory(files, depth)
    except Exception as e:
        print(e)
    return files


def _get_files_from_directory(files, depth=0):
    if depth == -1:
        return
    for item in os.listdir():
        if item.startswith("$"):
            continue

        if os.path.isfile(item):
            file = File(item, os.path.abspath(item), os.path.getsize(item),
                        'file')
            files.append(file)

        if os.path.isdir(item):
            file = File(item, os.path.abspath(item), 0, 'dir')
            files.append(file)
            os.chdir(item)
            try:
                _get_files_from_directory(files, depth - 1)
            except Exception as e:
                print(e)
            os.chdir("..")


def _get_drivers():
    import win32api

    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    return drives


if __name__ == "__main__":
    for file in get_files():
        print(file)