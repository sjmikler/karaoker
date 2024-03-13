import os
from collections import namedtuple
from pathlib import Path

import yaml

SearchQuery = namedtuple("Search", ("artist", "song", "limit"))


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


def assert_constants_are_set():
    msg = "Please set the constants in the constants.yaml file"
    assert get_constant("MP4_DIRECTORY") != "/PATH/TO/MP4_DIRECTORY", msg
    assert get_constant("TXT_DIRECTORY") != "/PATH/TO/TXT_DIRECTORY", msg
    assert get_constant("FINAL_DIRECTORY") != "/PATH/TO/FINAL_DIRECTORY", msg


def parse_song_queries():
    songs_location = get_constant("SONG_LIST")
    songs = []

    with open(songs_location, "r") as file:
        lines = file.read().strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line = line.replace(";", "\t").split("\t")
            artist = line.pop(0).strip()
            title = line.pop(0).strip() if line else ""
            limit = line.pop(0).strip() if line else "1"
            songs.append(SearchQuery(artist, title, limit))
    return songs


def get_song_title(song, suffix=""):
    if suffix and not suffix.startswith("."):
        suffix = "." + suffix
    title = f"{song.artist} - {song.title}{suffix}"
    title = title.replace("/", "")
    return title
