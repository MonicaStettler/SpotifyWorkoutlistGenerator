"""Module that makes use of the Spotify Web API to retrieve pseudo-random songs based
or not on a given exiting Spotify genre 
"""

#Project is  under construction. Currently can extract the song name and artist of one 
#random song from the Spotify database and save to csv file. Working on extraction of features to build dataset.
#API connection code credited to

import sys
import json
import re
import requests
import base64
import urllib
import random

# Client Keys
CLIENT_ID = "e4017dbf1bf44a7f93f1f7767d5e8801"
CLIENT_SECRET = "4f12c8c91e654d23b0bd0e58324ef5d2"

# Spotify API URIs
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


def get_token():
    client_token = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET)
                                    .encode('UTF-8')).decode('ascii')

    headers = {"Authorization": "Basic {}".format(client_token)}
    payload = {
        "grant_type": "client_credentials"
    }
    token_request = requests.post(
        SPOTIFY_TOKEN_URL, data=payload, headers=headers)
    access_token = json.loads(token_request.text)["access_token"]
    return access_token


def request_valid_song(access_token, genre=None):
    # Wildcards for random search
    randomSongsArray = ['%25a%25', 'a%25', '%25a',
                        '%25e%25', 'e%25', '%25e',
                        '%25i%25', 'i%25', '%25i',
                        '%25o%25', 'o%25', '%25o',
                        '%25u%25', 'u%25', '%25u']
    print("Random Song array is:", randomSongsArray)

    randomSongs = random.choice(randomSongsArray)
    print("Track Id is:", randomSongs)
    # Genre filter definition
    if genre:
        genreSearchString = " genre:'{}'".format(genre)
    else:
        genreSearchString = ""
    # Upper limit for random search
    maxLimit = 10000
    while True:
        try:
            randomOffset = random.randint(1, maxLimit)
            authorization_header = {
                "Authorization": "Bearer {}".format(access_token)
            }
            song_request = requests.get(
                "{}/search?query={}&offset={}&limit=1&type=track".format(
                    SPOTIFY_API_URL,
                    randomSongs + genreSearchString,
                    randomOffset
                ),
                headers=authorization_header
            )
            song_info = json.loads(song_request.text)['tracks']['items'][0]
            artist = song_info['artists'][0]['name']
            id = song_info['artists'][0]['id']
            song = song_info['name']

            print("This is the song id:", id)

        except IndexError:
            if maxLimit > 1000:
                maxLimit = maxLimit - 1000
            elif maxLimit <= 1000 and maxLimit > 0:
                maxLimit = maxLimit - 10
            else:
                artist = "Rick Astley"
                song = "Never gonna give you up"
                break
            continue
        break
    return "{} - {}".format(artist, song), artist, song, id, randomSongs

def getFeatures(id, access_token):

# =============================================================================
#     authorization_header = {
#                 "Authorization": "Bearer {}".format(access_token)
#             }
# =============================================================================
    featureRequests = requests.get('https://api.spotify.com/v1/audio-features/?ids=' + id) #.format(id), headers = authorization_header)
    feature_info = json.loads(featureRequests.text) #['audio-features'] #['items'][0]

    #danceability = feature_info['danceability']
    #energy = feature_info['energy']
    #key = feature_info['key']
    #loudness = feature_info['loudness']
    #mode = feature_info['mode']
    #speechiness = feature_info['mode']
    #acousticness = feature_info['acousticness']
    #instrumentalness = feature_info['instrumentalness']
    #liveness = feature_info['liveness']
    #valence = feature_info['valence']
    #tempo2 = feature_info['tempo']
    #print("This is tempo:", tempo2)

    return feature_info

def save2csv(filename, artist,song, id, randomSongs):
    infile = open(filename, 'a')
    infile.write(artist + ',' + song + ',' + id + ',' +randomSongs + ',' + '\n')
    infile.close()


def main():
    args = sys.argv[1:]
    n_args = len(args)

    if n_args > 1:
        print('usage: py ./random_song.py [genre]')
        sys.exit(1)
    else:
        access_token = get_token()
        if n_args == 0:
            result, artist, song, id, randomSongs = request_valid_song(access_token)
        else:
            selected_genre = (re.sub('[^a-zA-Z0-9]', '', args[0])).lower()
            # Fix for 'Trap' genre based on some suggestions
            if (selected_genre == 'trap'):
                selected_genre = 'traplatino'
            try:
                with open('genres.json', 'r') as infile:
                    valid_genres = json.load(infile)
            except FileNotFoundError:
                print("Couldn't find genres file!")
                sys.exit(1)

            if selected_genre in valid_genres:
                result = request_valid_song(access_token, genre=selected_genre)
            else:
                result = request_valid_song(access_token)

        print(result)

        featureTest = getFeatures(id, access_token)
        
        print("This is from json:", featureTest)

        save2csv('randomSongList.csv', artist, song, id, randomSongs)


if __name__ == '__main__':
    main()
