FROM ninelvalentin/microskel

ENV REDIS_HOST=redis

ADD . /opt/service_weather
WORKDIR /opt/service_weather

RUN pip install -r requirements.txt

CMD ["python", "service_weather.py"]