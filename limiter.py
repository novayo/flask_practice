import datetime
import os
import redis

from flask import jsonify
from flask import request

TIME_FORMAT = r'%m/%d/%Y-%H:%M:%S'
REDIS_USERNAME = os.environ.get('REDIS_USERNAME')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
REDIS = redis.Redis(
    host='redis-14029.c1.asia-northeast1-1.gce.redns.redis-cloud.com',
    port=14029,
    decode_responses=True,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
)


def limit_in_a_minute(times):
    def decorator(func):
        def _inner(*args, **kwargs):
            ip = request.remote_addr

            now = datetime.datetime.now()
            ttls = REDIS.get(ip)
            if ttls is None:
                ttls = ''

            new_data = []
            for time_str in ttls.split(','):
                if not time_str:
                    continue
                time = datetime.datetime.strptime(time_str, TIME_FORMAT)
                if time >= now:
                    new_data.append(time_str)

            if len(new_data) + 1 > times:
                return jsonify({'message': 'Rate limit exceeded'}), 429

            new_data.append((now + datetime.timedelta(minutes=1)).strftime(TIME_FORMAT))
            REDIS.set(ip, ','.join(new_data))

            return func(*args, **kwargs)

        return _inner

    return decorator
