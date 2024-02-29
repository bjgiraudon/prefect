import os

from prefect import flow, task
import redis
from pydantic import SecretStr, BaseModel

REDIS_CLIENT_HOST = os.environ.get("REDIS_CLIENT_HOST", "localhost")
REDIS_CLIENT_PORT = int(os.environ.get("REDIS_CLIENT_PORT", "6379"))
REDIS_CLIENT_PASSWORD = SecretStr(os.environ.get("REDIS_CLIENT_PASSWORD", ""))
REDIS_STREAM_NAME = os.environ.get("REDIS_STREAM_NAME", "dedl:new_features")


class Event(BaseModel):
    collection: str
    feature: str
    geometry: str


@task(log_prints=True)
def add_event(redis: redis.Redis, stream: str, payload: Event):
    redis.xadd(stream, vars(payload))


@flow(name="Redis Stream Events", log_prints=True)
def send_events(
    host: str = REDIS_CLIENT_HOST,
    port: int = REDIS_CLIENT_PORT,
    password: SecretStr | None = REDIS_CLIENT_PASSWORD,
    stream: str = REDIS_STREAM_NAME,
    events: list[Event] = [],
) -> None:
    redis_client = redis.Redis(
        host=host,
        port=port,
        password=password,
        decode_responses=True,
    )

    for event in events:
        add_event(redis_client, stream, event)


if __name__ == "__main__":
    events = []
    for i in range(10):
        events.append(
            Event(
                collection="FOO",
                feature=f"BAR{i}",
                geometry='{"type": "Point", "coordinates": [0, 0]}',
            )
        )

    send_events(events=events)
