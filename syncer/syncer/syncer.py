
def sync_tracks(authorizer, cookie):

    next_track_page = "https://api.spotify.com/v1/me/tracks"
    while next_track_page:
        cur = authorizer.conn.cursor()
        user_id = authorizer.get_user_id(cookie)
        resp = authorizer.authorized_request(next_track_page,
                cookie)
        resp.raise_for_status()
        for track in resp.json()['items']:

            # add liked track if not present
            cur.execute("insert into catify.tracks ( spotify_id, "
                "spotify_name, spotify_href, spotify_explicit, "
                "spotify_uri, spotify_duration_ms) select "
                "%s, %s, %s, %s, %s, %s "
                "where not exists (select spotify_id from catify.tracks "
                "where spotify_id = %s )",
                (
                    track['track']['id'],
                    track['track']['name'],
                    track['track']['href'],
                    track['track']['explicit'],
                    track['track']['uri'],
                    track['track']['duration_ms'],
                    track['track']['id'],
                    ))
            authorizer.conn.commit()
            cur.execute("select id from catify.tracks where spotify_id "
                    "= %s",(track['track']['id'],))
            track_id = cur.fetchone()[0]
            
            # like liked track if like not present
            cur.execute("insert into catify.users_tracks (user_id,track_id,"
                "relationship) select %s, %s, 'SPOTIFY_LIKE' "
                "where not exists (select id from catify.users_tracks "
                "where user_id = %s and track_id = %s)", (
                    user_id,
                    track_id,
                    user_id,
                    track_id
                    ))

            # add artists if not present
            artist_ids = []
            for artist in track['track']['artists']:
                cur.execute("insert into catify.artists (spotify_id, "
                        "spotify_name, spotify_href, spotify_uri) select "
                        "%s, %s, %s, %s where not exists (select spotify_id "
                        "from catify.artists where spotify_id = %s) " , (
                            artist['id'], artist['name'], artist['href'],
                            artist['uri'], artist['id'])) 
                authorizer.conn.commit()
                cur.execute("select id from catify.artists where spotify_id "
                        "= %s",(artist['id'],))
                artist_id = cur.fetchone()[0]
                artist_ids.append(artist_id)

            # link track to artists
            for artist_id in artist_ids:
                cur.execute("insert into catify.artists_tracks (track_id, "
                        "artist_id, relationship) select %s, %s, 'HAS' "
                        "where not exists (select id from "
                        "catify.artists_tracks where artist_id = %s and "
                        "track_id = %s)", (
                            track_id,
                            artist_id,
                            artist_id,
                            track_id,
                            ))
            authorizer.conn.commit()
        cur.close()
        next_track_page = resp.json()['next']
