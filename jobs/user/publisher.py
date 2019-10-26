from time import sleep
import authorizer
import pika

def get_cookie():
    auth = authorizer.Authorizer()
    cur = auth.conn.cursor()
    cur.execute("""
        select cookie from catify.users
        where synced_at < (current_timestamp - interval '4 hours')
        order by synced_at
        limit 1
    """)
    result = cur.fetchone()[0]
    cur.close()
    return result


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    while True:
        q = channel.queue_declare(queue='users_to_sync')
        cookie =  get_cookie()
        if cookie != '':
            channel.basic_publish(exchange='', routing_key='users_to_sync',
                body=cookie)
        sleep(1*60)

