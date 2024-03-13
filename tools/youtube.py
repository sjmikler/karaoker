import os
from pathlib import Path

import requests
from pytube import YouTube
from pytube.exceptions import AgeRestrictedError

from tools.utils import get_constant

MP4_DIRECTORY = os.path.join(get_constant("DATA_DIRECTORY"), "MP4")
JPG_DIRECTORY = os.path.join(get_constant("DATA_DIRECTORY"), "JPG")


def download_mp4(link, new_title=None, table=dict()):
    max_resolution = get_constant("PREFERRED_RESOLUTION")

    try:
        yt = YouTube(link)
        stream = yt.streams.get_by_resolution(max_resolution) or yt.streams.filter().get_highest_resolution()

    except AgeRestrictedError:
        yt = YouTube(
            link,
            use_oauth=True,
            allow_oauth_cache=True,
        )
        stream = yt.streams.get_by_resolution(max_resolution) or yt.streams.filter().get_highest_resolution()

    info = yt.vid_info
    author = info["videoDetails"]["author"]
    title = info["videoDetails"]["title"]

    if new_title is None:
        new_title = f"{author} - {title}"

    table["YT artist"] = author
    table["YT title"] = title
    table["quality"] = stream.resolution
    table["size MB"] = stream.filesize_mb

    if stream.exists_at_path(os.path.join(MP4_DIRECTORY, new_title)):
        table["missing"] = "false"
    else:
        table["missing"] = "true"
        stream.download(MP4_DIRECTORY, filename=new_title)

    thumbnail_destination = (Path(JPG_DIRECTORY) / new_title).with_suffix(".jpg")
    download_thumbnail(yt, thumbnail_destination)


def download_thumbnail(yt, destination):
    if os.path.exists(destination):
        return

    response = requests.get(yt.thumbnail_url)
    with open(destination, "wb") as file:
        file.write(response.content)
