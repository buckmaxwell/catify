
def login_user_from_cookie(conn, cookie):
    cur = conn.cursor()
    cur.execute('select id from catify.users where cookie=%s and'
            ' access_token_expiration > current_timestamp;', (cookie,))
    user_id_row = cur.fetchone()
    if not user_id_row:
        return False
    return user_id_row[0]
