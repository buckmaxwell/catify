
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
            # TODO: add correct user tracks not already in playlist to playlist
            pass

    return True


def create_playlist(authorizer, cookie, user_id, name):
    url = "https://api.spotify.com/v1/users/{}/playlists".format(
            user_id)
    body_dict = { 'name': name, 'public': False,
            'description': 'created by catify' }
    return authorizer.authorized_post_request(url, cookie, body_dict)
