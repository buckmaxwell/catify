
if __name__ == '__main__':


    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='artist_genres')
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(handle_message, queue='artist_genres', no_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    main()
