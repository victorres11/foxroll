import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

# TODO: Redis or redistogo??
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# This grabs production redis url in heroku config vars, and fails over to a localhost i can use.
# redis_url = redis.from_url(os.environ.get("REDIS_URL"), 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
