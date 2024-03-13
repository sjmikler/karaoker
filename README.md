# karaoker

Mass download songs from https://usdb.animux.de/.

### Instructions

1. Login to animux and set your `PHPSESSID` cookie as an environment variable
2. Create a **song list** (explained below)
3. Set up correct paths in `constants.yaml`
4. Install all the requirements
5. Run `main.py`

> If you need to download age restricted youtube video, you will be prompted to login (via pytube).

### Explanation: song list

This is a list of all the songs you want to download.

Each line in this file is a download query in form:

```
ARTIST;TITLE;MAX_SONGS_TO_DOWNLOAD
```

* You can use query `ABBA;;10` to download 10 most popular `ABBA` songs.

* You can specify the title `AC/DC;Back in Black`, then the number of songs defaults to 1.

**Example file content**

```
a-ha;Take On Me
Abba;;10
AC/DC;Back in Black
AC/DC;Highway To Hell
Aerosmith;;4
Adele;Rolling In The Deep
Akurat;Lubię mówić z tobą
Adam Lambert;Whataya Want From Me

Tenacious D;;10
Three Days Grace;;10
Skillet;;5
Skillet;Feel Invincible
Alphaville;Forever Young
```


