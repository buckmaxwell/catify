
# strategy -- pull artists randomly and add to the queue.

import authorizer
import pika



def get_artists():
    auth = authorizer.Authorizer()
    cur = auth.conn.cursor()
    cur.execute("""
        select spotify_id from catify.artists order by random() limit 50;
    """)
    return ','.join([x[0] for x in cur])


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    q = channel.queue_declare(queue='artist_genres')
    for artist_id in get_artists():
        channel.basic_publish(exchange='', routing_key='artist_genres',
                body=artist_id)

