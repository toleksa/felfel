from flask import Flask
import redis
import os

from prometheus_client import make_wsgi_app, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# could (or should) be Counter, but for this case Gauge seems to be better
hit_count_gauge = Gauge("hit_count","HIT_COUNT value")
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

@app.route("/")
def index():
    username = os.environ["REDIS_USERNAME"]
    password = os.environ["REDIS_PASSWORD"]
    host = os.environ["REDIS_HOST"]
    port = os.environ["REDIS_PORT"]
    db = os.environ["REDIS_DB"]
    client = redis.Redis(
        username=username, password=password, host=host, port=port, db=db
    )
    key = "HIT_COUNT"
    count = int(client.get(key) or 0)
    hit_count_gauge.set(count)
    response = f"Hello FELFEL. The count is: {count}"
    client.set(key, count + 1)
    return response



# for kubernetes probes
@app.route("/health")
def health():
    return "", 200


app.run(host="0.0.0.0", port=8080)
