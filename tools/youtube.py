import os

import requests
from pytube import YouTube

from tools.utils import const


def _download_mp4(link: str, new_title: str, table=dict(), authenticate=False, only_audio=False):
    max_resolution = const.PREFERRED_RESOLUTION
    jpg_destination_path = os.path.join(const.DATA_DIRECTORY, "JPG", new_title) + ".jpg"
    mp4_destination_path = os.path.join(const.DATA_DIRECTORY, "MP4", new_title) + ".mp4"
    mp4_final_path = os.path.join(const.FINAL_DIRECTORY, new_title, new_title) + ".mp4"
    mp4_ok = os.path.exists(mp4_final_path) or os.path.exists(mp4_destination_path)
    if mp4_ok and os.path.exists(jpg_destination_path):
        return

    if authenticate:
        yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    else:
        yt = YouTube(link)

    if only_audio:
        stream = yt.streams.filter(only_audio=True).first()
    else:
        stream = yt.streams.get_by_resolution(max_resolution) or yt.streams.filter().get_highest_resolution()

    info = yt.vid_info
    author = info["videoDetails"]["author"]
    title = info["videoDetails"]["title"]

    table["YT artist"] = author
    table["YT title"] = title
    table["quality"] = stream.resolution
    table["size MB"] = stream.filesize_mb

    if not stream.exists_at_path(mp4_destination_path):
        MP4_DIRECTORY = os.path.join(const.DATA_DIRECTORY, "MP4")
        stream.download(MP4_DIRECTORY, filename=new_title + ".mp4")
    maybe_download_thumbnail(yt, jpg_destination_path)


def download_mp4(link, new_title, table=dict()):
    link = link.replace("embed/", "watch?v=")

    try:
        return _download_mp4(link, new_title, table, authenticate=False, only_audio=False)
    except Exception:
        pass
    if const.INTERACTIVE_AUTHENTICATION:
        try:
            return _download_mp4(link, new_title, table, authenticate=True, only_audio=False)
        except Exception:
            pass
        try:
            return _download_mp4(link, new_title, table, authenticate=True, only_audio=True)
        except Exception as e:
            print(e)
    else:
        try:
            return _download_mp4(link, new_title, table, authenticate=False, only_audio=True)
        except Exception as e:
            print(e)
    return 1  # non-zero return here means a failure


def maybe_download_thumbnail(yt, destination):
    if os.path.exists(destination):
        return

    response = requests.get(yt.thumbnail_url)
    with open(destination, "wb") as file:
        file.write(response.content)
