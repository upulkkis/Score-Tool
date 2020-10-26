from flask_caching import Cache
import flask
import uuid
server = flask.Flask(__name__)
cache=Cache()
CACHE_CONFIG={'CACHE_TYPE':'redis',
'CACHE_KEY_PREFIX':'server1',
'CACHE_REDIS_HOST':'localhost',
'CACHE_REDIS_PORT':'6379',
'CACHE_REDIS_URL': 'redis://localhost:6379'}
cache.init_app(server,config=CACHE_CONFIG)
cache.set('test', uuid.uuid4())
print(cache.get('tes'))
print(cache.get('test'))

