from time import sleep
import authorizer
import pika


def get_artists():
    auth = authorizer.Authorizer()
    cur = auth.conn.cursor()
    cur.execute("""
        select spotify_id from catify.artists

        where genres_updated_at < (current_timestamp - interval '12 hours')
        order by genres_updated_at

        limit 50;
    """)
    result = ','.join([x[0] for x in cur])
    cur.close()
    return result


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    while True:
        q = channel.queue_declare(queue='artist_genres')
        artist_ids =  get_artists()
        if artist_ids != '':
            channel.basic_publish(exchange='', routing_key='artist_genres',
                body=artist_ids)
        sleep(10)

