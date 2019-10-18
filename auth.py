from const import *
from psycopg2.extras import Json
from requests.auth import HTTPBasicAuth
import psycopg2
import requests
import arrow


class Authorizer:
    def __init__(self):

        self.conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                host=DB_HOST,
                port=DB_PORT)


    def close(self):
        self.conn.close()

    def user_exists(self, cookie):
        cur = self.conn.cursor()
        cur.execute('select id from catify.users where cookie=%s',
                (cookie,))
        user_id_row = cur.fetchone()
        cur.close()
        if not user_id_row:
            return False
        return True 

    def get_user_id(self, cookie):
        cur = self.conn.cursor()
        cur.execute('select id from catify.users where cookie=%s',
                (cookie,))
        user_id_row = cur.fetchone()
        cur.close()
        if not user_id_row:
            return False
        return user_id_row[0] 

    def get_access_token(self, cookie):
        cur = self.conn.cursor()
        cur.execute('select access_token from catify.users where cookie=%s',
                (cookie,))
        access_id_row = cur.fetchone()
        cur.close()
        if not access_id_row:
            return False
        return access_id_row[0] 

    def user_loggedin(self, cookie):
        cur = self.conn.cursor()
        cur.execute('select id from catify.users where cookie=%s and'
                ' access_token_expiration > current_timestamp;', (cookie,))
        user_id_row = cur.fetchone()
        cur.close()
        if not user_id_row:
            return False
        return True 

    def user_refresh(self, cookie):
        cur = self.conn.cursor()
        cur.execute('select refresh_token from catify.users where cookie=%s',
                (cookie,))
        refresh_token_row = cur.fetchone()
        if not refresh_token_row:
            return False
        refresh_token = refresh_token_row[0]
        resp = requests.post('https://accounts.spotify.com/api/token',
                data={ 'grant_type':'refresh_token',
                    'refresh_token': refresh_token },
                auth=HTTPBasicAuth(SPOTIFY_CLIENT_ID,
                    SPOTIFY_CLIENT_SECRET))
        if resp.status_code == 200:
            access_token = resp.json()['access_token']
            expires = arrow.now().shift(seconds=resp.json()['expires_in']
                    ).datetime
            cur.execute('update catify.users set (access_token, '
                    ' access_token_expiration) = (%s, %s) where '
                    'cookie=%s', (access_token, expires, cookie))
            self.conn.commit()
            cur.close()
            return True
        return False


    def attempt_login_if_not_logged_in(self, cookie):
        # check if user exists
        if self.user_exists(cookie) and self.user_loggedin(cookie):
            return True
        elif self.user_exists(cookie) and not self.user_loggedin(cookie):
            return self.user_refresh(cookie)
        elif not self.user_exists(cookie):
            return False
        # check if user is logged in


    def spotify_find_or_create_user_helper(self, access_token, refresh_token,
            access_expiration):
        """Returns cookie, or false"""
        resp = requests.get('https://api.spotify.com/v1/me',
                headers={'Authorization': 'Bearer {}'.format(
                    access_token)})
        if resp.status_code != 200:
            return False 

        email = resp.json()['email']
        account_type = 'spotify'
        profile = resp.json()
        cur = self.conn.cursor()
        cur.execute("select cookie from catify.users where email = %s", (email,))
        user_cookie_row = cur.fetchone()

        # The user exists
        if user_cookie_row:
            cur.execute("update catify.users set ( access_token,"
                " refresh_token, access_token_expiration, profile) = (%s,"
                " %s, %s, %s)", ( access_token,
                    refresh_token, access_expiration, Json(profile) ))
            self.conn.commit()
            return user_cookie_row[0]

        # The user does not exist yet
        cur.execute("insert into catify.users (id, email, account_type, access_token,"
                " refresh_token, access_token_expiration, profile) values (default, %s,"
                " %s, %s, %s, %s, %s) returning cookie", (email, account_type, access_token,
                    refresh_token, access_expiration, Json(profile) ))
        self.conn.commit()
        user_cookie_row = cur.fetchone()
        cur.close()
        return user_cookie_row[0]

    def spotify_find_or_create_user(self, code):
        """Returns cookie, or false"""

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
            cookie =  self.spotify_find_or_create_user_helper(access, refresh, expires)
            if cookie:
                return cookie
        return False 

    def authorized_request(self, url, cookie):
        self.attempt_login_if_not_logged_in(cookie)
        access_token = self.get_access_token(cookie)
        resp = requests.get(url, 
                headers={'Authorization': 'Bearer {}'.format(
                    access_token)})
        return resp



