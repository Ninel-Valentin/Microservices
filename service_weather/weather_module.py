from flask import request

import json
import datetime
import redis
from decouple import config


client = redis.Redis(host=config("REDIS_HOST", "redis"))


def configure_views(app):
    @app.route("/weather", methods=["GET"])
    def weather():
        city = request.args.get("city")
        date = request.args.get("date", str(datetime.date.today()))
        key = f"{city}-{date}" if date else city
        weather = client.get(key)
        print(f"key={key}")
        if not weather:
            return "No data", 401

        print(f"weather = {weather}")
        weather = client.get(key).decode("utf-8")
        weather = json.loads(weather)
        return json.dumps(weather), 200

    @app.route("/weather", methods=["POST"])
    def create():
        keys = ("temperature", "humidity", "wind")
        weather = {k: request.form.get(k) for k in keys}
        city = request.form.get("city", "Brasov")
        date = request.form.get("date", str(datetime.date.today()))
        key = f"{city}-{date}" if date else city
        client.set(key, json.dumps(weather))

        return "OK", 200
