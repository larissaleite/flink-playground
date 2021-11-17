from kafka import KafkaProducer
import json
from datetime import datetime
import random
from uuid import uuid4
import pycountry

KAFKA_TOPIC = "user.events.v1"

producer = KafkaProducer(
    bootstrap_servers="kafka:29092",
    value_serializer=lambda v: json.dumps(v).encode("ascii"),
)

while True:
    producer.send(
        KAFKA_TOPIC,
        value={
            "event_id": uuid4().hex,
            "event_timestamp": datetime.now().strftime("%Y-%m-%d %H-%M-%S.%m"),
            "platform": random.choice(["ios", "web", "android"]),
            "user_id": uuid4().hex,
            "country": random.choices(list(pycountry.countries))[0].alpha_3,
        },
    )
    producer.flush()
