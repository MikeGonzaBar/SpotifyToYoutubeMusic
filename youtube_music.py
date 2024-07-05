from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from typing import List, Dict, Any
import time 

SCOPES = ["https://www.googleapis.com/auth/youtube"]

from dotenv import load_dotenv
load_dotenv()

CLIENT_SECRETS_FILE = 'client_secret_208967776625-182tae4nnmh59pf7474kffmemkqna9p7.apps.googleusercontent.com.json'

class YouTubeMusicClient:
    def __init__(self):
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=8080)
        self.client = build('youtube', 'v3', credentials=credentials)
        self.searchQueriesResponses = {}
        
    def fetch_playlists(self) -> List[Dict[str, Any]]:
        request = self.client.playlists().list(part="snippet,contentDetails", mine=True, maxResults=50)
        response = request.execute()
        return response.get('items', [])
    
    def print_youtube_music_playlists(self, playlists: List[Dict[str, Any]]):
        for playlist in playlists:
            print(f"YouTube Music - Name: {playlist['snippet']['title']}, ID: {playlist['id']}")
            
    def search_song(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for a song on YouTube Music by query. Uses cached responses to minimize API calls.

        :param query: The search query string (song name and artist).
        :return: A list of dictionaries containing song information.
        """
        print(f"SEARCHING FOR SONG: {query}")  # Debug print
        # Check if the query already exists in the cache
        if query in self.searchQueriesResponses:
            print(f"\tUsing cached result for query: {query}")  # Debug print
            return self.searchQueriesResponses[query]
        else:
            search_response = self.client.search().list(
                q=query,
                part="snippet",
                maxResults=1,
                type="video"
            ).execute()
            time.sleep(0.1)  # Delay to avoid hitting the rate limit
            songs = [
                {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnails': item['snippet']['thumbnails'],
                }
                for item in search_response.get('items', [])
            ]

            # Cache the result for future queries
            self.searchQueriesResponses[query] = songs
            print(f"\tFounded songs")  # Debug print
            return songs
    
    def create_playlist(self, title: str, description: str) -> str:
        """
        Create a new playlist on YouTube Music.

        :param title: The title of the playlist.
        :param description: The description of the playlist.
        :return: The ID of the newly created playlist.
        """
        print(f"CREATING PLAYLIST: {title}")  # Debug print
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
        time.sleep(1)
        print(f"\tPlaylist created successfully. ID: {response['id']}")  # Debug print
        return response['id']

    def add_song_to_playlist(self, playlist_id: str, video_id: str):
        """
        Add a song to a specified playlist on YouTube Music.

        :param playlist_id: The ID of the playlist to add the song to.
        :param video_id: The video ID of the song to add.
        """
        print(f"Adding song with video ID {video_id} to playlist {playlist_id}")  # Debug print
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
        response = add_request.execute()
        time.sleep(1)
        print(f"\tSong added successfully. Item ID: {response['id']}")  # Debug print
        
    def fetch_playlist_songs(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Fetch songs from a specified YouTube Music playlist.

        :param playlist_id: The ID of the playlist to fetch songs from.
        :return: A list of dictionaries, each containing information about a song.
        """
        print(f"FETCHING SONGS FROM PLAYLIST ID: {playlist_id}")  # Debug print
        songs = []
        request = self.client.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50  # Adjust based on your needs
        )
        while request:
            response = request.execute()
            time.sleep(1)
            for item in response.get('items', []):
                songs.append({
                    'id': item['snippet']['resourceId']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnails': item['snippet']['thumbnails'],
                })
            # Check if there's a next page
            request = self.client.playlistItems().list_next(request, response)
        print(f"\tSuccessfully fetched {len(songs)} songs from playlist.")
        return songs
        
    def find_playlist_by_name(self, target_name: str) -> str:
        """
        Find a YouTube Music playlist by name.

        :param target_name: The name of the playlist to find.
        :return: The ID of the matching playlist if found, otherwise None.
        """
        print(f"SEARCHING FOR PLAYLIST WITH NAME: {target_name}")  # Debug print
        playlists = self.fetch_playlists()
        for playlist in playlists:
            if playlist['snippet']['title'].lower() == target_name.lower():
                print(f"\tPlaylist found: {playlist['id']}")  # Debug print
                return playlist['id']
        print("Playlist not found.")
        return None
                    
    def create_youtube_playlists_from_spotify(self, spotify_playlists):
        try:
            if not spotify_playlists:
                print("No playlists found in Spotify.")
                return

            print("Starting to create YouTube playlists from Spotify playlists.")  # Debug print
            for playlist in spotify_playlists:
                title = playlist['name']
                tracks = playlist['tracks']  # Get all the tracks
                print(f"Processing Spotify playlist: {title}")  # Debug print

                # Check if a playlist with the same name already exists on YouTube Music
                existing_playlist_id = self.find_playlist_by_name(title)
                if existing_playlist_id:
                    print(f"Playlist '{title}' already exists on YouTube Music.")  # Debug print
                    #TODO: CREATE FUNCTION THAT CHECKS SONGS IN PLAYLIST AND ADDS THEM IF NOT FOUND
                    continue
                else:
                    # Create a new playlist on YouTube Music
                    print(f"Creating new playlist '{title}' on YouTube Music.")  # Debug print
                    new_playlist_id = self.create_playlist(title, "Playlist created from Spotify")
                    # Add the first 3 songs to the new playlist
                    for track in tracks:
                        song_name = track['name']
                        song_artists = ', '.join(artist for artist in track['artists'])
                        search_query = f"{song_name} {song_artists}"
                        search_result = self.search_song(search_query)
                        if search_result:
                            youtube_song_id = search_result[0]['id']
                            self.add_song_to_playlist(new_playlist_id, youtube_song_id)
                        else:
                            print(f"Song '{song_name}' by '{song_artists}' not found on YouTube Music.")
                    print(f"Playlist '{title}' created on YouTube Music from Spotify.")
        except Exception as e:
            print(f"Failed to create YouTube playlists from Spotify: {e}")  # Error handling