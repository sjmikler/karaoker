import os
from collections import namedtuple
from pathlib import Path

import yaml

Query = namedtuple("Query", ("artist", "title", "limit", "language"))


class ConstantGetter:
    def __init__(self, yaml_path):
        self._reload_variables(yaml_path)

    def _reload_variables(self, yaml_path):
        if not os.path.exists(yaml_path):
            raise KeyError(f"File {yaml_path} does not exist")

        self.yaml_path = yaml_path
        self.variables = yaml.safe_load(open(yaml_path))

    def _get_constant(self, key) -> str:
        # check if variable is defined in the environment
        if os.environ.get(key):
            return os.environ.get(key)

        # otherwise see the yaml file settings
        if key in self.variables:
            return self.variables[key]
        else:
            raise KeyError(f"Variable {key} not found in {self.yaml_path}")

    def __getattr__(self, key):
        return self._get_constant(key)

    def __getitem__(self, key):
        return self._get_constant(key)


def package_relative_path(path):
    """Returns the absolute path of a file relative to the library."""
    parent_path = Path(__file__).absolute().parent.parent
    return str(parent_path.joinpath(path))


def assert_constant_paths_exist(*required_paths):
    for key in required_paths:
        value = const[key]
        assert os.path.exists(value), f"Variable {key} is not set or file does not exist: {value}"


def parse_song_query(query):
    query = query.replace(";", "\t").split("\t")
    artist = query.pop(0).strip()
    title = query.pop(0).strip() if query else ""
    limit = query.pop(0).strip() if query else "1"
    language = query.pop(0).strip() if query else ""
    return Query(artist, title, limit, language)


def parse_song_queries():
    songs_location = const.SONG_LIST
    queries = []

    with open(songs_location, "r") as file:
        lines = file.read().strip().split("\n")

        for line in lines:
            line = line.strip()
            line = line.split("#")[0].strip()
            if not line:
                continue

            query = parse_song_query(line)
            if query not in queries:
                queries.append(query)
            else:
                print(f"Duplicated query: {query}")
    return queries


def remove_trailing_dots(path):
    """Trailing dots are not allowed in directory names in Windows. Remove them."""
    parts = os.path.normpath(path).split(os.sep)
    for i, part in enumerate(parts):
        # remove trailing dots
        parts[i] = part.rstrip(".")

    name = parts[-1]
    stem = Path(name).stem
    suffix = Path(name).suffix
    if stem.endswith("."):
        stem = stem.rstrip(".")
    parts[-1] = stem + suffix
    return os.sep.join(parts)


def sanitize_path(path):
    """Removing characters that are not allowed in file paths, including Windows."""
    path = path.replace("?", "")
    return remove_trailing_dots(path)


def sanitize_name(name):
    """Removing characters that are not allowed in file names, including Windows."""
    name = name.replace("/", "")
    return sanitize_path(name)


def get_song_title(song, suffix=""):
    if suffix and not suffix.startswith("."):
        suffix = "." + suffix
    title = f"{song.artist} - {song.title}{suffix}"
    return sanitize_name(title)


def exists_with_the_same_size(source, target):
    return os.path.exists(target) and os.path.getsize(source) == os.path.getsize(target)


default_yaml_location = package_relative_path("constants.yaml")
const = ConstantGetter(default_yaml_location)
