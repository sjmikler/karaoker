# karaoker

Mass download karaoke songs for UltraStar from https://usdb.animux.de/.

UltraStar Deluxe: https://github.com/UltraStar-Deluxe/USDX

### Instructions

1. Login to animux and set your `PHPSESSID` cookie as an environment variable
2. Create a **song list** (explained below)
3. Set up correct paths in `constants.yaml`
4. Install all the requirements
5. Run `main.py`

> If you try to download age restricted youtube video, the download will fail.
> To proceed, set INTERACTIVE_AUTHENTICATION=true, then you will be prompted to login (via pytube).

Whatever you set as `FINAL_DIRECTORY` is ready to be used by UltraStar.

Your existing songs will not be affected. Existing files will not be overriden.

### Explanation: song list

This is a list of all the songs you want to download.

Each line in this file is a download query in form:

```
ARTIST;TITLE;MAX_SONGS_TO_DOWNLOAD;LANGUAGE
```

You can leave some of the fields blank.
If more than 1 song matches your query, they will be sorted in the order of popularity.
For example:

* You can use query `ABBA;;10` to download 10 most popular `ABBA` songs.
* You can specify the title `AC/DC;Back in Black`, then the number of songs defaults to 1.
* You can use `;;10;english` to download 10 most popular english songs.

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

### Other options

---

You can download songs without creating **song list**:

```
python main.py "adele;;5" "system of a down;B.Y.O.B"
```

---

You can specify different `constants.yaml` file:

```
python main.py --constants /PATH/TO/CONSTANTS.yaml
```

---
