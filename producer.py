from confluent_kafka import Producer
import requests
import json
import time

def read_config():
    # reads the producer configuration from producer.properties
    # and returns it as a key-value map
    config = {}
    with open("client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    return config

def get_bus_arrivals(stop_id, app_key):
    # fetches bus arrival data from the TfL API
    url = f"https://api.tfl.gov.uk/StopPoint/{stop_id}/Arrivals?app_key={app_key}"
    response = requests.get(url)
    return response.json()

def produce(topic, config, stop_id, app_key):
    # creates a new producer instance
    producer = Producer(config)

    try:
        while True:
            # fetches bus arrival data
            arrivals = get_bus_arrivals(stop_id, app_key)


            for bus in arrivals:
                if isinstance(bus, dict):  # ensure it's a dictionary
                    key = bus.get("lineId", "unknown")
                    value = json.dumps(bus)
                    producer.produce(topic, key=key, value=value)
                    print(f"Produced message to topic {topic}: key = {key}, destination={bus.get('destinationName', '')}")
                else:
                    print("Unexpected data type from TfL API:", bus)
            # send any outstanding or buffered messages to the Kafka broker
            producer.flush()
            # wait for 60 seconds before fetching new data
            time.sleep(60)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    config = read_config()
    topic = "london_transport"
    stop_id = "490000254W"
    app_key = "4e209d567ba44f97b338ad3d7f2bdf4c"

    produce(topic, config, stop_id, app_key)