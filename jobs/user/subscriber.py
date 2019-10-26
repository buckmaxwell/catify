from psycopg2.extras import Json
import authorizer
import pika
import syncer


auth = authorizer.Authorizer()


def handle_message(ch, method, properties, body):
    # track spotify ids (comma separated)
    cookie = body.decode("utf-8")

    if cookie == '':
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    syncer.sync_tracks(auth, cookie)

    cur = auth.conn.cursor()
    cur.execute("""update catify.users set synced_at = current_timestamp
    where cookie = %s""",(cookie,))
    cur.close()
    auth.conn.commit()

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='users_to_sync')
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume('users_to_sync', handle_message, auto_ack=False)

    channel.start_consuming()
    main()
