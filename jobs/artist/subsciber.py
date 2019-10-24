import authorizer


auth = authorizer.Auth()


def link_genres_to_artist(spotify_artist_id, genres_list):
    cur = auth.conn.cursor()
    # Add genres if they don't exist
    for genre_name in genres_list:
        cur.execute("""insert into catify.genres (name) values
        %s where not exists ( select name from catify.genres
        where name = %s""", (genre_name, genre_name))
    auth.conn.commit()

    # Link artists to genre
    cur.execute("""select id from catify.artists where spotify_id = %s""",
            (spotify_artist_id,))
    artist_id = cur.fetchone()[0]

    for genre_name in genres_list:
        cur.execute("""select id from catify.genres where name = %s""",
                (genre_name,))
        genre_id = cur.fetchone()[0]
        cur.execute("""insert into catify.artists_genres (artist_id, genre_id)
        values (%s,%s)""", (artist_id, genre_id))
    auth.conn.commit()
    cur.close()


def update_artists(artist_dict):
    cur = auth.conn.cursor()
    cur.execute("""update catify.artists set popularity = %s
    where spotify_id = %s""", (artist_dict['popularity'],
        artist_dict['id']))
    auth.conn.commit()
    cur.close()


def handle_message(ch, method, properties, body):
    # artist spotify ids (comma separated)
    spotify_ids = body
    resp = auth.authorized_request('https://api.spotify.com/v1/artists',
            params={'ids': spotify_ids})
    for artist in resp.json()['artists']:
        link_genres_to_artist(artist['id'], artist['genres'])
        update_artists(artist)

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='artist_genres')
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(handle_message, queue='artist_genres', no_ack=False)

    channel.start_consuming()
    main()
