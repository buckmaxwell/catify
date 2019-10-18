import spotify_sender

def make_genre_playlists(conn, cookie):
    # send

    
    # add each track to tracks if not present
    add_liked_tracks(conn,cookie)

    # join all tracks to user


def add_liked_tracks(conn,cookie):
    next_track_page = "https://api.spotify.com/v1/me/tracks"
    while next_track_page:
        cur = conn.cursor()
        resp = spotify_sender.get(conn, next_track_page,
                cookie)
        if resp.status_code == 200:
            for track in resp.json()['items']:

                # add liked track if not present
                cur.execute("insert into catify.tracks (id, name, href,"
                    "explicit, uri, duration_ms) values (%s, %s, %s, %s, %s, %s)"
                    " where not exists (select id from catify.tracks where id = %s )",
                    (
                        track['track']['id'],
                        track['track']['name'],
                        track['track']['href'],
                        track['track']['explicit'],
                        track['track']['uri'],
                        track['track']['duration_ms'],
                        track['track']['id'],
                        ))
                
                # like liked track if like not present
                # TODO

                # add artists if not present
                # TODO

                # link track to artists
                # TODO

            next_track_page = resp.json()['next']
        else:
            break # surprise code, TODO: add retry logic
    conn.commit()
    cur.close()

def add_liked_albums(conn, cookie):
    # TODO
    pass




