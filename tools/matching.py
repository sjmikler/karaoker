import os
import shutil
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from moviepy.editor import AudioFileClip
from tqdm import tqdm

from tools import utils

MP4_DIRECTORY = os.path.join(utils.get_constant("DATA_DIRECTORY"), "MP4")
TXT_DIRECTORY = os.path.join(utils.get_constant("DATA_DIRECTORY"), "TXT")
JPG_DIRECTORY = os.path.join(utils.get_constant("DATA_DIRECTORY"), "JPG")
FINAL_DIRECTORY = utils.get_constant("FINAL_DIRECTORY")


def MP4ToMP3(mp4, mp3):
    converter = AudioFileClip(mp4)
    converter.write_audiofile(mp3, verbose=False, logger=None)
    converter.close()


def copy_and_convert(txt_path: str, mp4_path: str, destination: str):
    os.makedirs(destination, exist_ok=True)

    for file_name in os.listdir(txt_path):
        file_path = os.path.join(txt_path, file_name)
        file_dest = os.path.join(destination, file_name)
        if not os.path.exists(file_dest):
            shutil.copy(file_path, file_dest)

    mp4_dest = os.path.join(destination, os.path.basename(mp4_path))
    if not os.path.exists(mp4_dest):
        shutil.copy(mp4_path, mp4_dest)

    new_mp4_path = os.path.join(destination, Path(mp4_path).name)
    new_mp3_path = Path(new_mp4_path).with_suffix(".mp3")
    if not os.path.exists(new_mp3_path):
        MP4ToMP3(new_mp4_path, new_mp3_path)

    short_name = os.path.basename(txt_path)
    cover_name = f"{short_name} [CO].jpg"
    cover_path = os.path.join(destination, cover_name)
    thumbnail_path = os.path.join(JPG_DIRECTORY, short_name) + ".jpg"

    if not utils.exists_with_the_same_size(thumbnail_path, cover_path):
        if not os.path.exists(cover_path) or utils.get_constant("OVERWRITE_THUMBNAILS"):
            shutil.copy(thumbnail_path, cover_path)


def run_matching_and_conversion(songs):
    processes = []
    executor = ProcessPoolExecutor(max_workers=os.cpu_count())

    for song in songs:
        txt_name = utils.get_song_title(song)
        mp4_name = utils.get_song_title(song, suffix=".mp4")
        txt_path = os.path.join(TXT_DIRECTORY, txt_name)
        mp4_path = os.path.join(MP4_DIRECTORY, mp4_name)

        destination = os.path.join(FINAL_DIRECTORY, txt_name)
        proc = executor.submit(copy_and_convert, txt_path, mp4_path, destination)
        processes.append(proc)

    pbar = tqdm(total=len(songs), desc="Progress")
    while processes:
        num_processes = len(processes)
        finished = [proc for proc in processes if proc.done()]
        for p in finished:
            p.result()
            processes.remove(p)
        if finished:
            pbar.update(len(finished))
        time.sleep(0.1)
    pbar.close()
