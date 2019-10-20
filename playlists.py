
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

    # Create new playlists
    created_playlists = []
    for pl_name in playlists_to_create:
        resp = create_playlist(authorizer, cookie, user_id, pl_name) 
        created_playlists.append(resp.json()['id'])

    # Update playlist ids in preferences
    for i, genre in enumerate(genres):
        if genre['selected'] and not genre.get('spotify_playlist_id'):
            genre['spotify_playlist_id'] = created_playlists[i]
    new_preferences = preferences
    preferences['genres'] = genres
    cur.execute("""
    update catify.users set preferences = %s where cookie = %s""",
    (new_preferences, cookie))
    authorizer.conn.commit()

    # Add the songs to the playlist
    for genre in genres:
        if genre['selected']:
            # TODO: get the existing playlist
            tracks_in_playlist_already = get_track_ids_from_playlist(
                    authorizer, cookie, spotify_playlist_id)

            tracks_for_playlist = get_track_ids_for_genre(
                    authorizer, cookie, genre['name']) 
            # TODO: add correct user tracks not already in playlist to playlist
            pass

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

        join musicbrainz.artist m_artist on c_artist.spotify_name = m_artist.name
        join musicbrainz.artist_tag m_artist_tag on m_artist_tag.artist = m_artist.id
        join musicbrainz.tag m_tag on m_artist_tag.tag = m_tag.id

        where c_user.cookie = %s 
        and m_tag.name = %s
    """, (cookie, genre_name))
    result = [r[0] for r in cur]
    cur.close()
    return result


def get_track_ids_from_playlist(authorizer, cookie, spotify_playlist_id):
    url = "https://api.spotify.com/v1//playlists/{}".format(
            spotify_playlist_id)
    resp = authorizer.authorized_request(url, cookie)
    return [ t['id'] for t in resp.json()['tracks']]




def create_playlist(authorizer, cookie, user_id, name):
    url = "https://api.spotify.com/v1/users/{}/playlists".format(
            user_id)
    body_dict = { 'name': name, 'public': False,
            'description': 'created by catify' }
    return authorizer.authorized_post_request(url, cookie, body_dict)
