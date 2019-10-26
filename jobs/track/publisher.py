from time import sleep
import authorizer
import pika

# TODO: should be called get_tracks
def get_artists():
    auth = authorizer.Authorizer()
    cur = auth.conn.cursor()
    cur.execute("""
        select spotify_id from catify.tracks
        where audio_features_updated_at < (current_timestamp - interval '48 hours')
        order by audio_features_updated_at
        limit 100
    """)
    result = ','.join([x[0] for x in cur])
    cur.close()
    return result


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    while True:
        q = channel.queue_declare(queue='track_audio_features')
        artist_ids =  get_artists()
        if artist_ids != '':
            channel.basic_publish(exchange='', routing_key='track_audio_features',
                body=artist_ids)
        sleep(10)

