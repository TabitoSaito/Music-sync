from dotenv import set_key
from pathlib import Path

import ytmusicapi

from getpass import getpass

env_file_path = Path("src/config/.env")
env_file_path.touch(mode=0o600, exist_ok=True)

print("Welcome to the environment setup helper. For this project to work u need to setup a Spotify API, Youtube Music API and an Amazon Music acount.")
print("Let's start with the Spotify API.")
print("Follow this link https://developer.spotify.com/ and login to your Spotify account")
print("After logging in follow this link https://developer.spotify.com/dashboard and create a new app")
print("Fill out all necessary fields and select 'Web API'")
print("After pressing 'save' you will land on the dashboard of your new app. Now all you have to do is to copy the necessary data to the terminal")

client_id = input("CLIENT_ID: ")
set_key(dotenv_path=env_file_path, key_to_set="CLIENT_ID", value_to_set=client_id)
client_secret = input("CLIENT_SECRET: ")
set_key(dotenv_path=env_file_path, key_to_set="CLIENT_SECRET", value_to_set=client_secret)
redirect_uri = input("REDIRECT_URI: ")
set_key(dotenv_path=env_file_path, key_to_set="REDIRECT_URI", value_to_set=redirect_uri)

print("Ok your Spotify API is set up.")
print("Now you have to input your Spotify user id.")
print("Here is a post that helps you find your user id https://support.dittomusic.com/en/articles/6701098-how-do-i-find-my-spotify-id")

spotify_user_id = input("SPOTIFY_USER_ID: ")
set_key(dotenv_path=env_file_path, key_to_set="SPOTIFY_USER_ID", value_to_set=spotify_user_id)

print("And now we are done with Spotify")
print("Lets continue with Youtube Music")
print("First you need to get your Youtube user id")
print("Here is a post that helps you find your user id https://support.google.com/youtube/answer/3250431?hl=en")
print("be carful we need the user id and not the channel id")

youtube_user_id = input("YOUTUBE_USER_ID: ")
set_key(dotenv_path=env_file_path, key_to_set="YOUTUBE_USER_ID", value_to_set=youtube_user_id)

print("Because the unofficial Youtube Music API from sigma67 is used in this process a browser.json file has to be created to authenticate")
print("Follow this guide https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html to find the raw header response and copy it into the terminal")
while True:
    try:
        ytmusicapi.setup("browser.json")
        break
    except Exception as e:
        print(e)

print("Ok that's that")
print("Last but not least Amazone Music")
print("Due to no publicly accessible API this project uses Selenium to syncronieze Amazon Music playlists")
print("For that reason all we need are your login information")
print("So you don't have to manually input your user info every time the data will be saved in the .env file")

email = input("EMAIL: ")
set_key(dotenv_path=env_file_path, key_to_set="EMAIL", value_to_set=email)

password = getpass("PASSWORD")
set_key(dotenv_path=env_file_path, key_to_set="PASSWORD", value_to_set=password)

print("Now you are done and the project is ready to run.")
print("To check if everything is working correctly you can run tui_test.py")
