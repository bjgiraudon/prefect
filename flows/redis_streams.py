import os

from prefect import flow, task
import redis
from redis.typing import FieldT, EncodableT

REDIS_CLIENT_HOST = os.environ.get("REDIS_CLIENT_HOST", "localhost")
REDIS_CLIENT_PORT = int(os.environ.get("REDIS_CLIENT_PORT", "6379"))
REDIS_CLIENT_PASSWORD = os.environ.get("REDIS_CLIENT_PASSWORD", None)
REDIS_STREAM_NAME = os.environ.get("REDIS_STREAM_NAME", "dedl:new_features")


@task(log_prints=True)
def add_event(redis: redis.Redis, stream: str, payload: dict[FieldT, EncodableT]):
    redis.xadd(stream, payload)


@flow(name="Redis Stream Events", log_prints=True)
def send_events(
    redis: redis.Redis, stream: str, events: list[dict[FieldT, EncodableT]]
):
    for event in events:
        add_event(redis, stream, event)


if __name__ == "__main__":
    r = redis.Redis(
        host=REDIS_CLIENT_HOST,
        port=REDIS_CLIENT_PORT,
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
