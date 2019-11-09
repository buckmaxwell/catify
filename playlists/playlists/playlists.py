from psycopg2.extras import Json

def make_genre_playlists(authorizer, cookie):
    cur = authorizer.conn.cursor()

    cur.execute("""
    select profile->'id',preferences from catify.users where
    cookie = %s""", (cookie,))

    row = cur.fetchone()
    user_id, preferences = row

    genres = preferences.get('genres',[])
    playlists_to_create = []
    for genre in genres:
        if genre['selected'] and not genre.get('spotify_playlist_id'):
            playlists_to_create.append(genre['name'])
            resp = create_playlist(authorizer, cookie,
                    user_id, genre['name']) 
            genre['spotify_playlist_id'] = resp.json()['id']

    new_preferences = preferences
    preferences['genres'] = genres
    cur.execute("""
    update catify.users set preferences = %s where cookie = %s""",
    (Json(new_preferences), cookie))
    authorizer.conn.commit()

    # Add the songs to the playlist
    for genre in genres:
        if genre['selected']:

            tracks_in_playlist_already = get_track_ids_from_playlist(
                    authorizer, cookie, genre['spotify_playlist_id'])

            tracks_for_playlist = get_track_ids_for_genre(
                    authorizer, cookie, genre['name'])

            tracks_to_add = []
            already_contains = set(tracks_in_playlist_already)
            for track_for_playlist in tracks_for_playlist:
                if track_for_playlist in already_contains:
                    continue
                tracks_to_add.append(track_for_playlist)

            # add the tracks to the playlist
            add_tracks_to_playlist(authorizer, cookie,
                genre['spotify_playlist_id'], tracks_to_add)

    return True


def get_track_ids_for_genre(authorizer, cookie, genre_name):
    cur = authorizer.conn.cursor()
    cur.execute("""
    select c_track.spotify_id
        from catify.users c_user
        join catify.users_tracks c_user_track on c_user_track.user_id = c_user.id
        join catify.tracks c_track on c_user_track.track_id = c_track.id
        join catify.artists_tracks c_artist_track on c_artist_track.track_id = c_track.id
        join catify.artists c_artist on c_artist.id = c_artist_track.artist_id

        join catify.artists_genres c_artist_genre on c_artist.id = c_artist_genre.artist_id
        join catify.genres c_genre on c_genre.id = c_artist_genre.genre_id

        where c_user.cookie = %s 
        and c_genre.name = %s
    """, (cookie, genre_name))
    result = [r[0] for r in cur]
    cur.close()
    return result


def get_track_ids_from_playlist(authorizer, cookie, spotify_playlist_id):
    url = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            spotify_playlist_id)
    resp = authorizer.authorized_request(url, cookie)
    return [ t['track']['id'] for t in resp.json()['items']]


def add_tracks_to_playlist(authorizer, cookie, spotify_playlist_id, spotify_track_ids):
    url = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            spotify_playlist_id)
    body_dict = {'uris': [ 'spotify:track:{}'.format(sid) for sid in spotify_track_ids]}
    return authorizer.authorized_post_request(url, cookie, body_dict)


def create_playlist(authorizer, cookie, user_id, name):
    url = "https://api.spotify.com/v1/users/{}/playlists".format(
            user_id)
    name = "Catify's {}".format(name)
    body_dict = { 'name': name, 'public': False,
            'description': 'created by catify' }
    return authorizer.authorized_post_request(url, cookie, body_dict)


