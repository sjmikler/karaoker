# karaoker

Mass download karaoke songs from https://usdb.animux.de/.

### Instructions

Prerequisites:
* Python >= 3.6
* [UltraStar Deluxe](https://github.com/UltraStar-Deluxe/USDX) or other compatible karaoke game

Preparation:

1. Login to animux and note down your `PHPSESSID` cookie (using developer settings, section `storage`)
2. Set up correct paths and variables in `constants.yaml` (alternatively set corresponding environment variables)
3. Install the requirements to your python environment using `pip install -r requirements.txt`
4. Optionally create a **song list**, see section below

> If you try to download age restricted youtube video, the download will fail.
> To proceed, set INTERACTIVE_AUTHENTICATION=true, then you will be prompted to login (via [pytube](https://github.com/pytube/pytube)).

Whatever you set as `FINAL_DIRECTORY` is ready to be used by UltraStar Deluxe.
Your existing songs will not be affected. Files existing in `FINAL_DIRECTORY` will not be overriden.
For example, if you modify song offset in an already downloaded `.txt` file, it will not be overriden by karaoker.

When you are ready, run

```
python main.py
```

to download all songs from the song list or 

```
python main.py "ARTIST1;TITLE1" "ARTIST2;TITLE2;NUMBER;LANGUAGE" ...
```
to download a songs without using song list.

### Explanation: song list

This is a list of all the songs you want to download.
You don't need to create it, but using it will help you to recreate your song library whenver you need.

Each line in this file is a download query in form:

```
ARTIST;TITLE;MAX_SONGS_TO_DOWNLOAD;LANGUAGE
```

You can leave some of the fields blank.
If more than 1 song matches your query, they will be sorted in the order of popularity on animux and downloaded.
For example:

* You can use query `ABBA;;10` to download 10 most popular `ABBA` songs
* You can specify the title like `AC/DC;Back in Black`, then the number of songs to download defaults to 1
* You can use `;;10;english` to download 10 most popular english songs

**Example song list content**

```
# My favourite songs
Skillet;;5
Skillet;Feel Invincible
Andrzej Zaucha;Gumisie

# Hits that everyone knows
;;20;english
;;20;polish

# Songs for my dad
Abba;;10
AC/DC;Back in Black
AC/DC;Highway To Hell
Aerosmith;;4
Aerosmith;Cryin’
```

### Troubleshotting

**Q:** How do I find PHPSESSID?
* [instructions for Chrome](https://www.cookieserve.com/knowledge-base/website-cookies/how-do-i-check-cookies-in-chrome/)
* [instructions for Firefox](https://www.cookieserve.com/knowledge-base/website-cookies/how-do-i-check-cookies-in-firefox/)

### Other options
---

You can specify different `constants.yaml` file:

```
python main.py --constants /PATH/TO/CONSTANTS.yaml
```

---
