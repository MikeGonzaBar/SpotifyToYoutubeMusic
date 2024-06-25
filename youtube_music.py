from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from typing import List, Dict, Any

SCOPES = ["https://www.googleapis.com/auth/youtube"]

from dotenv import load_dotenv
load_dotenv()

CLIENT_SECRETS_FILE = 'client_secret_208967776625-182tae4nnmh59pf7474kffmemkqna9p7.apps.googleusercontent.com.json'

class YouTubeMusicClient:
    def __init__(self):
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=8080)
        self.client = build('youtube', 'v3', credentials=credentials)
        
    def fetch_playlists(self) -> List[Dict[str, Any]]:
        request = self.client.playlists().list(part="snippet,contentDetails", mine=True, maxResults=50)
        response = request.execute()
        return response.get('items', [])
    
    def print_youtube_music_playlists(self, playlists: List[Dict[str, Any]]):
        for playlist in playlists:
            print(f"YouTube Music - Name: {playlist['snippet']['title']}, ID: {playlist['id']}")
            
    def search_song(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for a song on YouTube Music by query.
        
        :param query: The search query string (song name and artist).
        :return: A list of dictionaries containing song information.
        """
        search_response = self.client.search().list(
            q=query,
            part="snippet",
            maxResults=1,
            type="video"
        ).execute()

        songs = []
        for item in search_response.get('items', []):
            songs.append({
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnails': item['snippet']['thumbnails']
            })
        
        return songs
    
    def create_playlist(self, title: str, description: str) -> str:
        """
        Create a new playlist on YouTube Music.

        :param title: The title of the playlist.
        :param description: The description of the playlist.
        :return: The ID of the newly created playlist.
        """
        create_playlist_body = {
            "snippet": {
                "title": title,
                "description": description,
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
        create_request = self.client.playlists().insert(
            part="snippet,status",
            body=create_playlist_body
        )
        response = create_request.execute()
        return response['id']

    def add_song_to_playlist(self, playlist_id: str, video_id: str):
        """
        Add a song to a specified playlist on YouTube Music.

        :param playlist_id: The ID of the playlist to add the song to.
        :param video_id: The video ID of the song to add.
        """
        add_video_body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        add_request = self.client.playlistItems().insert(
            part="snippet",
            body=add_video_body
        )
        add_request.execute()
                
    def create_youtube_test_playlist_from_spotify(self, title, spotify_playlists):
        if not spotify_playlists or not spotify_playlists[-1]['tracks']:
            print("No playlists or tracks found in Spotify.")
            return
        last_playlist = spotify_playlists[-1]
        last_song = last_playlist['tracks'][-1]
        song_name = last_song['name']
        song_artists = ', '.join(artist for artist in last_song['artists'])
        
        search_query = f"{song_name} {song_artists}"
        search_result = self.search_song(search_query)
        if not search_result:
            print("Song not found on YouTube Music.")
            return
        # Assuming search_result is a list of songs and we take the first match
        youtube_song_id = search_result[0]['id']
        
        # Create a new playlist on YouTube Music
        playlist_name = "Test Playlist from Spotify's Last Song"
        new_playlist_id = self.create_playlist(playlist_name, "Created from Spotify's last song in the last playlist.")
        
        # Add the song to the new playlist
        self.add_song_to_playlist(new_playlist_id, youtube_song_id)
        
        print(f"Playlist '{playlist_name}' created on YouTube Music with the song '{song_name}' by '{song_artists}'.")
        