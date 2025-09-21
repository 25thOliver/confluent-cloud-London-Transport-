from confluent_kafka import Consumer

def read_config():
    # reads the consumer configuration from consumer.properties
    # and returns it as a key-value map
    config = {}
    with open("client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    return config

def consume(topic, config):
    config["group.id"] = "london_transport_group"
    config["auto.offset.reset"] = "earliest"

    # creates a new consumer instance
    consumer = Consumer(config)
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is not None and msg.error() is None:
                key = msg.key().decode("utf-8") if msg.key() else "null"
                value = msg.value().decode("utf-8") if msg.value() else "null"
                print(f"Consumed message from {topic}: key={key}, value={value}")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    config = read_config()
    topic = "london_transport"
    consume(topic, config)