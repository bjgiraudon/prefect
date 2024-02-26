from prefect import flow, task
# import geojson
import redis
import os

REDIS_STREAM_NAME = os.environ.get("REDIS_STREAM_NAME", "new:features")

@task(log_prints=True)
def add_event(redis: redis.Redis, stream: str, payload: dict[redis.FieldT, redis.EncodableT]):
    redis.xadd(stream, payload)

@flow(name="Redis Stream Events")
def send_events(redis: redis.Redis, stream: str, events: list[dict[redis.FieldT, redis.EncodableT]]):
    for event in events:
        add_event(redis, stream, event)

if __name__ == "__main__":
    r = redis.Redis(
        host="localhost",
        port=6379,
        password=os.environ.get("REDIS_CLIENT_PASSWORD"),
        decode_responses=True)

    events = [
        {
            "collection": "FOO",
            "feature": "BAR",
            "geometry": '{"type": "Point", "coordinates": [0, 0]}',
        }
    ]
    
    send_events(r, REDIS_STREAM_NAME, events=events)
