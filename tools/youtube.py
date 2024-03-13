from os.path import join

from pytube import YouTube
from pytube.exceptions import AgeRestrictedError

from tools.utils import get_constant


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

    if stream.exists_at_path(join(get_constant("MP4_DIRECTORY"), new_title)):
        table["missing"] = "false"
    else:
        table["missing"] = "true"
        stream.download(get_constant("MP4_DIRECTORY"), filename=new_title)
