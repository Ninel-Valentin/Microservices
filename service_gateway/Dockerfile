FROM ninelvalentin/microskel

ADD . /opt/service_gateway
WORKDIR /opt/service_gateway

RUN pip install -r requirements.txt

CMD ["python", "service_gateway.py"]
