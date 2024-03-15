import os
import shutil
import tempfile
import zipfile
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

from tools import utils
from tools.utils import const

session = requests.Session()
AnimuxSong = namedtuple("AnimuxSong", ("artist", "title", "id", "views"))


def seach_songs(query, order="views", ud="desc", table=dict()):
    session.cookies.set("PHPSESSID", const.PHPSESSID)
    search_url = "https://usdb.animux.de/?link=list"
    params = {
        "interpret": query.artist,
        "title": query.title,
        "edition": "",
        "language": query.language,
        "order": order,
        "ud": ud,
        "limit": query.limit,
    }
    response = session.get(search_url, params=params)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    song_rows = soup.find("tr", {"class": "list_head"})
    song_rows = [row for row in song_rows if "?link=detail&amp;id=" in str(row)]
    if len(song_rows) == 0:
        return None

    return_songs = []
    for song_row in song_rows:
        cells = song_row.find_all("td")
        song_id = "".join([x for x in cells[1].find("a")["href"] if x.isdigit()])

        song = AnimuxSong(
            cells[0].text,
            cells[1].text,
            song_id,
            cells[6].text,
        )
        return_songs.append(song)
    return return_songs


def extract_youtube_link_for_id(id, table=dict()):
    session.cookies.set("PHPSESSID", const.PHPSESSID)
    search_url = f"https://usdb.animux.de/?link=detail&id={id}"
    soup = BeautifulSoup(session.get(search_url).text, "html.parser")
    links = soup.find_all("iframe", {"class": "embed"})
    if len(links) == 0:
        return None
    link = links[0]["src"]
    return link


def unpack_sanitized(zip_file, destination):
    """Unpacks all the files one by one, sanitizing the filenames when unpacking."""
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        for file in zip_ref.namelist():
            sanitized_path = utils.sanitize_path(file)
            final_path = os.path.join(destination, sanitized_path)
            os.makedirs(os.path.dirname(final_path), exist_ok=True)

            # Extract the file content and write it to the new sanitized path
            with zip_ref.open(file) as source, open(final_path, "wb") as target:
                shutil.copyfileobj(source, target)


def _download_annotations(songs):
    session.cookies.set("PHPSESSID", const.PHPSESSID)
    song_ids = [song.id for song in songs]
    new_archiv = "|".join(song_ids) + "|"
    session.cookies.set("ziparchiv", new_archiv)
    session.cookies.set("counter", str(len(song_ids)))
    soup = BeautifulSoup(session.get("https://usdb.animux.de/?link=ziparchiv").text, "html.parser")

    download_soup = BeautifulSoup(session.get("https://usdb.animux.de/?link=ziparchiv&save=1").text, "html.parser")
    links = [link for link in download_soup.find_all("a", href=True) if "Playlist.zip" in str(link)]
    assert len(links) == 1

    link = links[0]["href"]
    response = session.get("https://usdb.animux.de/" + link)

    tmp_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".zip", delete=False)
    tmp_file.write(response.content)
    tmp_file.close()
    unpack_sanitized(tmp_file.name, os.path.join(const.DATA_DIRECTORY, "TXT"))
    os.unlink(tmp_file.name)


def download_annotations_for_songs(songs, max_pack_size=10):
    missing_songs = []
    for song in songs:
        animux_compliant_title = f"{song.artist} - {song.title}"
        output_path = os.path.join(const.DATA_DIRECTORY, "TXT", animux_compliant_title)
        if not os.path.exists(output_path):
            missing_songs.append(song)

    for i in range(0, len(missing_songs), max_pack_size):
        _download_annotations(missing_songs[i : i + max_pack_size])
    return len(missing_songs)
