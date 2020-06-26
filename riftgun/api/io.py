"""
An API for interacting with JSON
"""
import json


def _unsafe_dump(fp, data, **kwargs):
    with open(fp, "w") as wfile:
        json.dump(data, wfile, **kwargs)


def write(filepath: str, data: dict, *, safe: bool = True, dump_kwargs: dict = None):
    """
    Writes provided JSON data to a JSON file.

    :param filepath: the path to the JSON file to write to.
    :param data: The new raw dictionary to write to the file.
    :param safe: Whether to do an sql "rollback" in case of failure to dump. Defaults to True.
    :param dump_kwargs: The kwargs (in a dictionary) to pass to json.dump()
    :return: None
    :raises: InterruptedError if dumping fails and safe is True
    """
    if safe:
        backup = read(filepath)
        try:
            _unsafe_dump(filepath, data, **dump_kwargs)
        except Exception as e:
            _unsafe_dump(filepath, backup)
            raise InterruptedError from e
        else:
            return
    else:
        _unsafe_dump(filepath, data, **dump_kwargs)


def read(filepath: str) -> dict:
    """
    Reads from a JSON file.

    :param filepath: the file path to read from
    :return:
    """
    with open("filepath") as rfile:
        data = json.load(rfile)
    return data


def merge(*dicts):
    """
    Merges as many dicts together as you want!

    :param dicts: a list of dictionaries.
    :return: the merged dictionary
    """
    new = {}
    for d in dicts:
        new.update(d)
    return new


class Cache:
    """
    A basic caching system. You should only need 1 of these per file.
    """

    def __init__(self, filepath: str, data: dict = None, *, name: str = None):
        self.fp = filepath
        self._raw_data = data
        if not data:
            self._raw_data = read(filepath)
        self.name = name

    def __repr__(self):
        return f"<Cache filepath='{self.fp}' size={len(self._raw_data)} name={self.name}>"

    def __setattr__(self, key, value):
        self._raw_data[key] = value

    def __getattr__(self, item):
        return self._raw_data[item]

    def get(self, item, default = None):
        return self._raw_data.get(item, default)

    @property
    def data(self) -> dict:
        return self._raw_data

    def refresh(self):
        """
        Refreshes the cache and loads from file.

        :return:
        """
        self._raw_data = read(self.fp)

    def __str__(self):
        return self.name

    def __add__(self, other):
        if not isinstance(other, (dict, type(self))):
            raise TypeError("Unsupported operand type(s) for +: 'Cache/dict' and '{}'".format(type(other).__name__))
        self._raw_data = merge(self.data, other)

    def __mul__(self, other):
        self.__add__(other)

    def dump(self):
        """Writes all cached data to {fp}"""
        write(self.fp, self.data)
