
def sync_tracks(authorizer, cookie):

    next_track_page = "https://api.spotify.com/v1/me/tracks"
    while next_track_page:
        cur = authorizer.conn.cursor()
        resp = authorizer.authorized_request(next_track_page,
                cookie)
        user_id = authorizer.get_user_id(cookie)
        if resp.status_code == 200:
            for track in resp.json()['items']:

                # add liked track if not present
                cur.execute("insert into catify.tracks (id, spotify_id, "
                    "spotify_name, sportify_href, spotify_explicit, "
                    "spotify_uri, spotify_duration_ms) values "
                    "(DEFAULT, %s, %s, %s, %s, %s, %s) "
                    "where not exists (select spotify_id from catify.tracks "
                    "where spotify_id = %s ) returning id",
                    (
                        track['track']['id'],
                        track['track']['name'],
                        track['track']['href'],
                        track['track']['explicit'],
                        track['track']['uri'],
                        track['track']['duration_ms'],
                        track['track']['id'],
                        ))
                track_id = cur.fetchone()[0]
                
                # like liked track if like not present
                cur.execute("insert into catify.users_tracks (user_id,track_id,"
                    "relationship) values (%s, %s, 'SPOTIFY_LIKE') "
                    "where not exists (select id from catify.users_tracks "
                    "where user_id = %s and track_id = %s)", (
                        user_id,
                        track_id,
                        user_id,
                        track_id
                        ))

                # add artists if not present
                # TODO

                # link track to artists
                # TODO

            next_track_page = resp.json()['next']
        else:
            break # surprise code, TODO: add retry logic
    authorizer.conn.commit()
    cur.close()
