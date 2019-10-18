import requests


def get(conn, uri, cookie):
    # TODO: this shouldn't talk to auth
    access_token = auth.login_user_if_not_logged_in(conn, cookie)
    resp = requests.get(uri, headers={'Authorization': 'Bearer {}'.format(
                access_token)})
    return resp




