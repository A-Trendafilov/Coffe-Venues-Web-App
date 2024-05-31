from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Place(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    rating: Mapped[str] = mapped_column(String(10), nullable=False)
    place_id: Mapped[str] = mapped_column(String(50), nullable=False)
    lat: Mapped[str] = mapped_column(String(50), nullable=False)
    lng: Mapped[str] = mapped_column(String(50), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
