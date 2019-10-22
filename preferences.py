from psycopg2.extras import Json


def add_new_possible_playlists(authorizer, cookie):
    cur = authorizer.conn.cursor()

    cur.execute("""
    select preferences from catify.users u where u.cookie = %s
    """, (cookie,))
    old_preferences = cur.fetchone()[0]

    cur.execute("""
    select * from (
    select tag_name, count(*) cnt from (select distinct m_tag.name tag_name, c_track.spotify_name
       from musicbrainz.recording m_track

       join catify.tracks c_track on m_track.name = c_track.spotify_name
       join catify.artists_tracks c_artist_track on c_track.id = c_artist_track.track_id
       join catify.artists c_artist on c_artist.id = c_artist_track.artist_id
       join catify.users_tracks c_user_track on c_user_track.track_id = c_track.id

       join musicbrainz.artist m_artist on c_artist.spotify_name = m_artist.name
       join musicbrainz.artist_tag m_artist_tag on m_artist_tag.artist = m_artist.id
       join musicbrainz.tag m_tag on m_artist_tag.tag = m_tag.id

       where m_artist.name ~* concat('\m',c_artist.spotify_name,'\M')
       and c_user_track.user_id = (
        select id from catify.users c_users where c_users.cookie = %s
       )) tab1 group by tag_name order by cnt desc) tab2 where cnt > 9 limit 500;
    """,(cookie,))

    old_genre_hash =  {}
    for genre in old_preferences.get('genres', []):
        old_genre_hash[genre['name']] = genre 

    new_preferences = old_preferences 
    new_preferences['genres'] = []
    for row in cur:
        genre_name, song_count = row[0], row[1]
        previous_entry = old_genre_hash.get(genre_name)
        if previous_entry:
            previous_entry['song_count'] = song_count
            new_preferences['genres'].append(previous_entry)
            continue
        new_preferences['genres'].append({
            'name': genre_name,
            'song_count': song_count,
            'selected': False
        })

    cur.execute("""
    update catify.users set preferences = %s where cookie = %s
    """, (Json(new_preferences), cookie))
    cur.close()
    authorizer.conn.commit()

    
def get_user_preferences(authorizer,cookie):
    cur = authorizer.conn.cursor()
    cur.execute("""
    select preferences from catify.users where cookie = %s
    """, (cookie,))
    return cur.fetchone()[0]


def select_genres(authorizer, cookie, genres):
    cur = authorizer.conn.cursor()
    prefs = get_user_preferences(authorizer, cookie)
    for genre in prefs['genres']:
        if genre['name'] in genres:
            genre['selected'] = True
        else:
            genre['selected'] = False


    cur.execute("""
    update catify.users set preferences = %s where cookie = %s
    """, (Json(prefs), cookie))
    cur.close()
    authorizer.conn.commit()






