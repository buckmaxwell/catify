import os


SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_STATE = 'prevent_cross_site_request_forgery55'
SPOTIFY_REDIRECT_URI = 'http://167.99.7.55:5000/spotify'
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']

SPOTIFY_API_SCOPES = [
        'playlist-modify-private',
        'playlist-modify-public',
        'playlist-read-collaborative',
        'playlist-read-private',
        'user-library-modify',
        'user-library-read',
        'user-read-email',
        'user-read-recently-played',
        'user-top-read',
        ]
