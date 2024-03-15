import argparse
import os

from progress_table import ProgressTable

from tools import animux, matching, metadata, utils, youtube
from tools.utils import const

PACK_PREPARATION_INTERVAL = 20


def prepare_packs(finished_songs):
    print(f"Processed {len(finished_songs)} songs. Downloading missing txt...", end=" ")
    num_missing = animux.download_annotations_for_songs(finished_songs, max_pack_size=10)
    print(f"Downloaded {num_missing}!")

    print("Creating packs and converting MP4 to MP3...")
    matching.run_matching_and_conversion(finished_songs)

    print("Processing metadata...", end=" ")
    for song in finished_songs:
        path = os.path.join(const.FINAL_DIRECTORY, utils.get_song_title(song))
        metadata.set_correct_audio_video_name(path)
    print("Finished!")


def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("songs", help="Pass songs in the command line instead of using songs file", nargs="*")
    parser.add_argument("--constants", default=None, help="Path to the constants file")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_command_line_arguments()
    if args.constants:
        const._reload_variables(args.constants)

    utils.assert_constant_paths_exist("DATA_DIRECTORY", "FINAL_DIRECTORY")
    assert const.PHPSESSID is not None, "PHPSESSID cookie is not set"

    if args.songs:
        queries = [utils.parse_song_query(song) for song in args.songs]
    else:
        utils.assert_constant_paths_exist("SONG_LIST")
        queries = utils.parse_song_queries()

    for subdir in ["MP4", "TXT", "JPG"]:
        path = os.path.join(const.DATA_DIRECTORY, subdir)
        os.makedirs(path, exist_ok=True)

    table = ProgressTable(
        num_decimal_places=1,
        pbar_show_progress=True,
        pbar_show_throughput=False,
    )
    table.add_column("artist")
    table.add_column("title")
    table.add_column("num", width=3)
    table.add_column("AX id")
    table.add_column("AX artist")
    table.add_column("AX title")
    table.add_column("views", width=5)
    table.add_column("YT artist")
    table.add_column("YT title")
    table.add_column("quality")
    table.add_column("size MB")

    num_songs_queried = sum([int(query.limit) for query in queries])
    print(f"Found {len(queries)} download queries, totaling {num_songs_queried} songs")

    pbar = table.pbar(num_songs_queried)
    good_song_counter = 0
    finished_songs = []

    for query in queries:
        table["artist"] = query.artist
        table["title"] = query.title

        songs = animux.seach_songs(query, table=table)
        if not songs:
            table["num"] = 0
            table.next_row(color="red")
            continue
        table["num"] = len(songs)

        for song in songs:
            if song in finished_songs:
                table.next_row(color="yellow")
                continue

            table["AX id"] = song.id
            table["AX artist"] = song.artist
            table["AX title"] = song.title
            table["views"] = song.views

            link = animux.extract_youtube_link_for_id(song.id, table=table)
            if link is None:
                table.next_row(color="red")
                continue

            animux_compliant_name = utils.get_song_title(song)
            result = youtube.download_mp4(link, new_title=animux_compliant_name, table=table)
            if result:
                table.next_row(color="red")
                continue

            finished_songs.append(song)
            good_song_counter += 1
            table.next_row()
            pbar.update(1)

        if len(finished_songs) >= PACK_PREPARATION_INTERVAL:
            table.close(close_pbars=False)
            prepare_packs(finished_songs)
            finished_songs = []
    table.close()
    if finished_songs:
        prepare_packs(finished_songs)

    print(f"Finished {good_song_counter} out of {num_songs_queried} queried")
