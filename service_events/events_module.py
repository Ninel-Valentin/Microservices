from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
import datetime

from microskel.db_module import Base


class Event(Base):
    __tablename__ = "event"  # mandatory
    id = Column(Integer, primary_key=True)
    city = Column(String(128))  # varchar
    date = Column(Date)
    name = Column(String(256))
    description = Column(Text)
    # Text = nelimitat, nu are o lungime fixa, precum String

    def to_dict(self):
        d = {}
        for k in self.__dict__.keys():
            if "_state" not in k:
                d[k] = self.__dict__[k] if "date" not in k else str(self.__dict__[k])
        return d


def configure_views(app):
    @app.route("/events", methods=["GET"])
    def events(db: SQLAlchemy):
        city = request.args.get("city")
        date = request.args.get("date")
        events = db.session.query(Event)
        if city:
            events = events.filter(Event.city == city)
        if date:
            events = events.filter(Event.date == date)
        return [e.to_dict() for e in events.all()], 200

    @app.route("/events", methods=["POST"])
    def create(db: SQLAlchemy):
        city = request.form.get("city", "Brasov")
        name = request.form.get("name")
        description = request.form.get("description")
        date = request.form.get("date")
        date = datetime.date(*[int(s) for s in date.split("-")]) if date else None
        event = Event(city=city, name=name, description=description, date=date)
        db.session.add(event)
        db.session.commit()
        return str(event.id), 201
        # return "OK", 201

    @app.route("/events/<id>", methods=["PUT"])
    def update(id, db: SQLAlchemy):
        try:
            id = int(id)
        except ValueError as e:
            return "Invalid ID", 402
        city = request.form.get("city")
        name = request.form.get("name")
        description = request.form.get("description")
        date = request.form.get("date")
        date = (
            datetime.date(*[int(s) for s in date.split("-")])
            if date
            else datetime.date.today()
        )
        event = db.session.query(Event).filter(Event.id == id)
        if event:
            event = event.first()
            event.city = city if city else event.city
            event.name = name if name else event.name
            event.description = description if description else event.description
            event.date = date if date else event.date
            db.session.commit()
            return "Ok", 201
        return "Not found", 404

    @app.route("/events/<id>", methods=["DELETE"])
    def delete():
        pass
