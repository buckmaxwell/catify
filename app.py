from flask import Flask, jsonify, request, redirect, make_response
from functools import wraps
from psycopg2.extras import Json
from requests.auth import HTTPBasicAuth
import arrow
import os
import psycopg2
import requests
import urllib
import auth

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

app = Flask(__name__)


conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cookie = request.cookies.get('catify0')
        if auth.login_user_from_cookie(conn, cookie):
            return f(*args, **kwargs)
        return redirect('/spotify-login', code=302)
    return decorated_function


def spotify_find_or_create_user(access_token, refresh_token, access_expiration):
    resp = requests.get('https://api.spotify.com/v1/me',
            headers={'Authorization': 'Bearer {}'.format(
                access_token)})
    if resp.status_code != 200:
        return 'There was a problem :(' 

    email = resp.json()['email']
    account_type = 'spotify'
    profile = resp.json()
    cur = conn.cursor()
    cur.execute("select cookie from catify.users where email = %s", (email,))
    user_cookie_row = cur.fetchone()
    if user_cookie_row:
        cur.execute("update catify.users set ( access_token,"
            " refresh_token, access_token_expiration, profile) = (%s,"
            " %s, %s, %s)", ( access_token,
                refresh_token, access_expiration, Json(profile) ))
        conn.commit()
        return user_cookie_row[0]
    cur.execute("insert into catify.users (id, email, account_type, access_token,"
            " refresh_token, access_token_expiration, profile) values (default, %s,"
            " %s, %s, %s, %s, %s) returning cookie", (email, account_type, access_token,
                refresh_token, access_expiration, Json(profile) ))
    conn.commit()
    user_cookie_row = cur.fetchone()
    cur.close()
    return user_cookie_row[0]



def spotify_request_tokens(code):
    resp = requests.post('https://accounts.spotify.com/api/token',
            data = {
                'grant_type': "authorization_code",
                'code': code,
                'redirect_uri': SPOTIFY_REDIRECT_URI
                },
            auth = HTTPBasicAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
            )
    if resp.status_code == 200:
        access = resp.json()['access_token']
        scope = resp.json()['scope']
        expires = arrow.now().shift(seconds=resp.json()['expires_in']).datetime
        refresh = resp.json()['refresh_token']
        user_cookie = spotify_find_or_create_user(access, refresh, expires)
        return user_cookie
    else:
        return False 

@app.route('/')
@login_required
def index():
    return 'you are logged in boy'

@app.route('/spotify-login')
def spotify_login():

    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'state': SPOTIFY_STATE,
        'scope': ' '.join(SPOTIFY_API_SCOPES),
        'show_dialog': 'false'
        }
    new_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(params)
    return redirect(new_url, code=302)

@app.route('/spotify')
def spotify():
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    if code is not None and state == SPOTIFY_STATE:
        cookie = spotify_request_tokens(code)
        if cookie:
            # result = make_response(render_template('index.html', foo=42))
            result = make_response("you are logged in")
            result.set_cookie('catify0', cookie)
            return result
    return 'you are not logged in'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
