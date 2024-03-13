import os

import requests
from pytube import YouTube
from pytube.exceptions import AgeRestrictedError

from tools.utils import get_constant

MP4_DIRECTORY = os.path.join(get_constant("DATA_DIRECTORY"), "MP4")
JPG_DIRECTORY = os.path.join(get_constant("DATA_DIRECTORY"), "JPG")
FINAL_DIRECTORY = os.path.join(get_constant("FINAL_DIRECTORY"))


def download_mp4(link, new_title, table=dict()):
    max_resolution = get_constant("PREFERRED_RESOLUTION")
    jpg_destination_path = os.path.join(JPG_DIRECTORY, new_title) + ".jpg"
    mp4_destination_path = os.path.join(MP4_DIRECTORY, new_title) + ".mp4"
    mp4_final_path = os.path.join(FINAL_DIRECTORY, new_title, new_title) + ".mp4"
    mp4_ok = os.path.exists(mp4_final_path) or os.path.exists(mp4_destination_path)
    if mp4_ok and os.path.exists(jpg_destination_path):
        return

    try:
        yt = YouTube(link)
        stream = yt.streams.get_by_resolution(max_resolution) or yt.streams.filter().get_highest_resolution()

    except AgeRestrictedError:
        # if the video is age restricted, we need to authenticate
        yt = YouTube(
            link,
            use_oauth=True,
            allow_oauth_cache=True,
        )
        stream = yt.streams.get_by_resolution(max_resolution) or yt.streams.filter().get_highest_resolution()

    info = yt.vid_info
    author = info["videoDetails"]["author"]
    title = info["videoDetails"]["title"]

    table["YT artist"] = author
    table["YT title"] = title
    table["quality"] = stream.resolution
    table["size MB"] = stream.filesize_mb

    if not stream.exists_at_path(mp4_destination_path):
        stream.download(MP4_DIRECTORY, filename=new_title + ".mp4")

    maybe_download_thumbnail(yt, jpg_destination_path)


def maybe_download_thumbnail(yt, destination):
    if os.path.exists(destination):
        return

    response = requests.get(yt.thumbnail_url)
    with open(destination, "wb") as file:
        file.write(response.content)
