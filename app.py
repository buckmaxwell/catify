from const import *
from flask import Flask, jsonify, request
from flask import redirect, make_response, render_template
from functools import wraps
import auth
import genre_playlists
import syncer
import urllib


app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authorizer = auth.Authorizer()
        cookie = request.cookies.get('catify0')
        if authorizer.attempt_login_if_not_logged_in(cookie):
            authorizer.close()
            return f(*args, **kwargs)
        authorizer.close()
        return redirect('/spotify-login', code=302)
    return decorated_function


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/make-genre-playlists')
@login_required
def make_genre_playlists():
    # TODO: do this async, return 204
    cookie = request.cookies.get('catify0')
    authorizer = auth.Authorizer()
    syncer.sync_user_tracks(authorizer, cookie)
    playlists.make_genre_playlists(authorizer, cookie)
    authorizer.close()
    return 'genre playlists created'


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
        authorizer = auth.Authorizer()
        cookie = authorizer.spotify_find_or_create_user(code)
        authorizer.close()
        if cookie:
            result = make_response(render_template('index.html'))
            result.set_cookie('catify0', cookie)
            return result
    return 'you are not logged in'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
