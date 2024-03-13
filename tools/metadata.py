from pathlib import Path


def extract_metadata_from_txt(txt_path):
    """Extracts metadata information from txt file.

    Example file
    #ARTIST:T. Love
    #TITLE:Chlopaki nie placza
    #MP3:T. Love - Chlopaki nie placza.mp3
    #CREATOR:rafallus
    #YEAR:1997
    #LANGUAGE:Polish
    #BPM:206.26
    #GAP:58060
    #VIDEO:v=X0lkrxFuGr8

    Outputs {"ARITSIT": "T. Love", ...}
    """
    try:
        with open(txt_path, encoding="UTF-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(txt_path, encoding="windows-1252") as f:
            content = f.read()

    data = {}
    for line in content.split("\n"):
        if not line:
            continue
        if line.startswith("#"):
            line = line[1:]
            key, value = line.split(":", 1)
            data[key] = value
    return data


def modify_metadata_to_txt(txt_path, new_metadata):
    """Modifies txt file.

    Replaces tag with appropriate values. Does not modify the rest of the file.
    """
    try:
        with open(txt_path, encoding="UTF-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(txt_path, encoding="windows-1252") as f:
            content = f.read()

    new_file = []
    for line in content.split("\n"):
        if line.startswith("#"):
            key, value = line.split(":", 1)
            if key[1:] in new_metadata:
                line = f"{key}:{new_metadata[key[1:]]}"
        new_file.append(line)

    with open(txt_path, "w", encoding="UTF-8") as f:
        f.write("\n".join(new_file))


def set_correct_audio_video_name(pack_location):
    path = Path(pack_location)
    assert path.is_dir(), f"{path} is not a directory"

    song_name = path.name
    file_path = path / song_name
    assert file_path.with_suffix(".txt").exists(), f"{file_path.with_suffix('.txt')} does not exist"
    assert file_path.with_suffix(".mp3").exists()
    assert file_path.with_suffix(".mp4").exists()

    txt_file = file_path.with_suffix(".txt")
    metadata = extract_metadata_from_txt(txt_file)
    metadata["MP3"] = f"{song_name}.mp3"
    metadata["VIDEO"] = f"{song_name}.mp4"
    modify_metadata_to_txt(txt_file, metadata)
