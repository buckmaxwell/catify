from psycopg2.extras import Json
import authorizer
import pika


auth = authorizer.Authorizer()


def add_audio_features_to_track(spotify_track_ids, audio_features_list):
    cur = auth.conn.cursor()
    
    for i,audio_features in enumerate(audio_features_list):

        cur.execute("""update catify.tracks set
        (spotify_audio_features,audio_features_updated_at) = (%s,
        current_timestamp) where spotify_id = %s""",(Json(audio_features),
            spotify_track_ids[i]))

    auth.conn.commit()

    cur.close()


def handle_message(ch, method, properties, body):
    # track spotify ids (comma separated)
    spotify_ids = body.decode("utf-8")

    if spotify_ids == '':
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    resp = auth.authorized_request(
            'https://api.spotify.com/v1/audio-features?ids={}'.format(
                spotify_ids))

    # audio features are returned in the order requested
    spotify_ids_list = spotify_ids.split(',')
    audio_features_list = resp.json()['audio_features']
    add_audio_features_to_track(spotify_ids_list, audio_features_list)

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='track_audio_features')
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume('track_audio_features', handle_message, auto_ack=False)

    channel.start_consuming()
    main()
