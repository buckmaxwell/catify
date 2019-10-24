import authorizer

auth = authorizer.Auth()


def link_genres_to_artist(spotify_artist_id, genres_list):
    # TODO implement
    pass

def handle_message(ch, method, properties, body):
    # artist spotify ids (comma separated)
    spotify_ids = body
    resp = auth.authorized_request('https://api.spotify.com/v1/artists',
            params={'ids': spotify_ids})
    for artist in resp.json()['artists']:
        link_genres_to_artist(artist['id'], artist['genres'])

    sentence_no = add_data_to_db(filename, int(filename.split('.')[-1]) )

    ch.basic_ack(delivery_tag=method.delivery_tag)
    q = channel.queue_declare(queue='completed')
    channel.basic_publish(exchange='', routing_key='completed', body=str(sentence_no))


if __name__ == '__main__':


    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='artist_genres')
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(handle_message, queue='artist_genres', no_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    main()
