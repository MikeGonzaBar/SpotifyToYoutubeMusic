from spotify import SpotifyClient
from youtube_music import YouTubeMusicClient

def main():
    spotify_client = SpotifyClient()
    # spotify_playlists = spotify_client.fetch_playlists()
    # print(spotify_playlists)
    # spotify_client.print_spotify_playlists(spotify_playlists)
    my_playlists = spotify_client.get_playlists_with_tracks()
    # print(spotify_client.get_playlists_with_tracks())

    youtube_music_client = YouTubeMusicClient()
    youtube_music_playlists = youtube_music_client.fetch_playlists()
    print(youtube_music_playlists)
    youtube_music_client.create_youtube_test_playlist_from_spotify("Test Playlist", my_playlists)
    youtube_music_playlists = youtube_music_client.fetch_playlists()
    print(youtube_music_playlists)
    # youtube_music_client.print_youtube_music_playlists(youtube_music_playlists)

if __name__ == "__main__":
    main()