## Music Synchronizer

This is my first python project using Machine learning. It's a simple program that synchronizes music playlists across services.

## Description

My project uses APIs and selenium to scrap playlists and determine what songs are missing. To match song names across platforms the program uses simple string comparison to try to find an exact match. If no match is found a Machine learning model is used to calculate the probability that two titles describe the same song. To do that, the difference between the count of every letter, number and symbol is calculated and parsed to the model.

## Features

- Supported platforms
  - Spotify
  - Youtube Music
  - Amazon Music
- Synchronize playlists by name across two or all platforms
- Automatically create and expand datasets with the necessary data from songs
- Evaluate different Machine learning models on song datasets

## Technologies

- **Spotify API (spotipy):** Used for fetching Spotify playlists, songs and to update fetched playlist. Also used to build dataset for Machine learning training.
- **Youtube Music API (ytmusicapi):** Used for fetching Youtube Music playlists, songs and to update fetched playlist. Also used to build dataset for Machine learning training.
- **Selenium:** Because Amazone music has no easily avalibal API, selenium is used to navigate the website. Used for fetching Amazon Music playlists, songs and to update fetched playlist. Also used to build dataset for Machine learning training.
- **pandas**: Used to manage and load Datasets for Machine learning models.
- **sklearn**: Used to train the Machine learning models.
- **joblib**: Used to save trained Machine learning models.

## Installation

### Clone Repository
```bash
git clone git@github.com:TabitoSaito/Music-sync.git
cd Music-sync
```

### Set Virtual Enviroment
```bash
python -m venv venv
source venv/bin/activate # (Windos: venv\Scripts\activate)
```
### Install Requiremantes
```bash
pip install -r requirements.txt
```

To use tests:

```bash
pip install -r requirements-dev.txt
```

Follow instructions in env_setup_help to setup all environment variables

```bash
python env_setup_help.py
```

## Usage example

```bash
python main.py
```

- Synchronies playlist with name "Sync" between Spotify and Amazon Music:<br>
  `>>>sync Sync spotify amazon`
- Synchronies playlist with name "Sync" between all services:<br>
  `>>>sync Sync`<br>
- create dataset with name "songs" and expand it with 5 tracks using Spotify and Youtube Music: <br>
  `>>>data new songs`<br>
  `>>>data load songs`<br>
  `>>>data expand spotify youtube 5`<br>
  output:<br>
  ```
  adding song 1/5
  adding song 2/5
  adding song 3/5
  adding song 4/5
  adding song 5/5
  >>>
  ```
  /data/raw/songs.csv
  ```csv
  ,platform1,platform2,name1,artist1,name2,artist2,same,ml guess
  0,spotify,youtube,Larg,Yll Limani,Po te pres te Shadervani,Yll Limani,,
  1,spotify,youtube,FBJ,ADAMEK,Oor Eh Peliculan,Armenian Navy Band,,
  2,spotify,youtube,Bella Napoli - Xtreme Sound Party Mix,Tobee,O mia bella Napoli,Peter Strothmann,,
  3,spotify,youtube,Wanted (feat. Emily N),TLF,Wanted 2018,Sportsalleen,,
  4,spotify,youtube,IDEMO [PART I],Svaba Ortak,ARKANUM [MASKEN PT. I],Svaba Ortak,,
  ```

## Challenges

- Collecting the needed data from the services
- Error handling with Selenium
- TUI designe

## Next Steps

- Add more parameters (like song length) to increase the accuracy of Machine learning models.
- Beautifying TUI
- Get access to the closed Amazon Music API and replace selenium approach
- Add more Tests

## Author
**Dominik Hölzl**</br>
[GitHub-Profil](https://github.com/TabitoSaito)
