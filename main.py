import os

from progress_table import ProgressTable

from tools import animux, matching, metadata, utils, youtube

PACK_PREPARATION_INTERVAL = 20


def prepare_packs(finished_songs):
    print(f"Processed {len(finished_songs)} songs. Downloading missing txt...", end=" ")
    num_missing = animux.download_annotations_for_songs(finished_songs, max_pack_size=10)
    print(f"Downloaded {num_missing}!")

    print("Creating packs and converting MP4 to MP3...")
    matching.run_matching_and_conversion(finished_songs)

    print("Processing metadata...", end=" ")
    for song in finished_songs:
        path = os.path.join(utils.get_constant("FINAL_DIRECTORY"), utils.get_song_title(song))
        metadata.set_correct_audio_video_name(path)
    print("Finished!")


if __name__ == "__main__":
    utils.assert_constants_are_correct()
    for subdir in ["MP4", "TXT", "JPG"]:
        path = os.path.join(utils.get_constant("DATA_DIRECTORY"), subdir)
        os.makedirs(path, exist_ok=True)

    table = ProgressTable(
        num_decimal_places=1,
        pbar_show_progress=True,
        pbar_show_throughput=False,
    )
    table.add_column("artist")
    table.add_column("title")
    table.add_column("num", width=3)
    table.add_column("views", width=5)

    queries = utils.parse_song_queries()
    num_songs = sum([int(query.limit) for query in queries])
    print(f"Found {len(queries)} download queries, totaling {num_songs} songs")

    pbar = table.pbar(num_songs)
    finished_songs = []

    for artist, title, limit in queries:
        table["artist"] = artist
        table["title"] = title

        songs = animux.seach_songs(artist, title, limit, table=table)
        if not songs:
            table["num"] = 0
            table.next_row(color="red")
            continue
        table["num"] = len(songs)

        for song in songs:
            table["AX id"] = song.id
            table["AX artist"] = song.artist
            table["AX title"] = song.title
            table["views"] = song.views

            link = animux.extract_youtube_link_for_id(song.id, table=table)
            if link is None:
                table.next_row(color="red")
                continue

            animux_compliant_title = utils.get_song_title(song, suffix=".mp4")
            youtube.download_mp4(link, new_title=animux_compliant_title, table=table)
            finished_songs.append(song)
            pbar.update(1)
            table.next_row()

        if len(finished_songs) >= PACK_PREPARATION_INTERVAL:
            table.close(close_pbars=False)
            prepare_packs(finished_songs)
            finished_songs = []
    table.close()
    prepare_packs(finished_songs)
