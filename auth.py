
def login_user_from_cookie(conn, cookie):
    cur = conn.cursor()
    cur.execute('select id from catify.users where cookie = %s', (cookie,))
    user_id_row = cur.fetchone()
    if user_id_row:
        return user_id_row[0]
    else:
        return False
