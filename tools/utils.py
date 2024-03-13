import os
from collections import namedtuple
from pathlib import Path

import yaml

Query = namedtuple("Query", ("artist", "song", "limit"))


def package_relative_path(path):
    """Returns the absolute path of a file relative to the library."""
    parent_path = Path(__file__).absolute().parent.parent
    return str(parent_path.joinpath(path))


YAML_PATH = package_relative_path("constants.yaml")
if not os.path.exists(YAML_PATH):
    raise KeyError(f"File {YAML_PATH} does not exist")

VARIABLES = yaml.safe_load(open(YAML_PATH))


def get_constant(key) -> str:
    # check if variable is defined in the environment
    if os.environ.get(key):
        return os.environ.get(key)

    # otherwise see the yaml file settings
    if key in VARIABLES:
        return VARIABLES[key]
    else:
        raise KeyError(f"Variable {key} not found in {YAML_PATH}")


def assert_constants_are_correct():
    required = ["DATA_DIRECTORY", "FINAL_DIRECTORY", "SONG_LIST"]

    for key in required:
        value = get_constant(key)
        assert os.path.exists(value), f"Variable {key} is not set or does not exist: {value}"


def parse_song_queries():
    songs_location = get_constant("SONG_LIST")
    songs = []

    with open(songs_location, "r") as file:
        lines = file.read().strip().split("\n")

        for line in lines:
            line = line.strip()
            line = line.split("#")[0].strip()
            if not line:
                continue

            line = line.replace(";", "\t").split("\t")
            artist = line.pop(0).strip()
            title = line.pop(0).strip() if line else ""
            limit = line.pop(0).strip() if line else "1"

            song = Query(artist, title, limit)
            if song not in songs:
                songs.append(song)
            else:
                print(f"Duplicated query: {song}")
    return songs


def get_song_title(song, suffix=""):
    if suffix and not suffix.startswith("."):
        suffix = "." + suffix
    title = f"{song.artist} - {song.title}{suffix}"
    title = title.replace("/", "")
    return title


def exists_with_the_same_size(source, target):
    return os.path.exists(target) and os.path.getsize(source) == os.path.getsize(target)
