import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_CLIENT_REDIRECT_URI')


class SpotifyClient:
    def __init__(self):
        self.client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                                                client_secret=SPOTIFY_CLIENT_SECRET,
                                                                redirect_uri=SPOTIFY_REDIRECT_URI,
                                                                scope='playlist-read-private'))

    def print_spotify_playlists(self, playlists: List[Dict[str, Any]]):
        for playlist in playlists:
            name = playlist['name']
            playlist_id = playlist['id']
            print(f"Spotify - Name: {name}, ID: {playlist_id}")
            tracks = self.client.playlist_tracks(playlist_id)
            for item in tracks['items']:
                track = item['track']
                track_name = track['name']
                artist_names = ', '.join([artist['name']
                                         for artist in track['artists']])
                print(f"\tTrack: {track_name}, Artist(s): {artist_names}")

    def fetch_playlists(self) -> List[Dict[str, Any]]:
        playlists = self.client.current_user_playlists()
        return playlists['items']
    
    def get_playlists_with_tracks(self) -> Dict[str, Dict[str, Any]]:
        playlists_info = []
        playlists = self.fetch_playlists()
        for playlist in playlists:
            print('Loading...')
            playlist_id = playlist['id']
            playlist_name = playlist['name']
            tracks_info = []
            tracks = self.client.playlist_tracks(playlist_id)
            for item in tracks['items']:
                track = item['track']
                track_name = track['name']
                artist_names = [artist['name'] for artist in track['artists']]
                tracks_info.append({"name": track_name, "artists": artist_names})
            playlists_info.append({"name": playlist_name, "tracks": tracks_info})
        return playlists_info
