from prefect import flow, task

# import geojson
import redis
from redis.typing import FieldT, EncodableT
import os

REDIS_STREAM_NAME = os.environ.get("REDIS_STREAM_NAME", "dedl:new_features")
REDIS_CLIENT_PASSWORD = os.environ.get("REDIS_CLIENT_PASSWORD", None)


@task(log_prints=True)
def add_event(redis: redis.Redis, stream: str, payload: dict[FieldT, EncodableT]):
    print(f"Redis XADD - stream_name:'{stream} with payload {payload}")
    redis.xadd(stream, payload)


@flow(name="Redis Stream Events", log_prints=True)
def send_events(
    redis: redis.Redis, stream: str, events: list[dict[FieldT, EncodableT]]
):
    for event in events:
        add_event(redis, stream, event)


if __name__ == "__main__":
    r = redis.Redis(
        host="localhost",
        port=6379,
        password=REDIS_CLIENT_PASSWORD,
        decode_responses=True,
    )

    events = []
    for i in range(10):
        events.append(
            {
                "collection": "FOO",
                "feature": f"BAR{i}",
                "geometry": '{"type": "Point", "coordinates": [0, 0]}',
            }
        )

    send_events(r, REDIS_STREAM_NAME, events=events)
