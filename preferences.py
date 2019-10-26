from psycopg2.extras import Json


def add_new_possible_playlists(authorizer, cookie):
    cur = authorizer.conn.cursor()

    cur.execute("""
    select preferences from catify.users u where u.cookie = %s
    """, (cookie,))
    old_preferences = cur.fetchone()[0]

    cur.execute("""
    select * from (select distinct genres.name, count(*) cnt from catify.users
        join catify.users_tracks ON users_tracks.user_id = users.id
        join catify.artists_tracks on users_tracks.track_id  = artists_tracks.track_id
        join catify.artists_genres on artists_genres.artist_id = artists_tracks.artist_id
        join catify.genres on genres.id = artists_genres.genre_id

        where users.cookie = %s
        group by genres.name
        ) tab1
        
        where cnt > 9 order by cnt desc;
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






