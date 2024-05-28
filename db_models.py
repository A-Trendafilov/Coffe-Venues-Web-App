from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Place(db.Model):
    __tablename__ = "places"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    place_id: Mapped[str] = mapped_column(String(50), nullable=False)
    lat: Mapped[float] = mapped_column(db.Float, nullable=False)
    lng: Mapped[float] = mapped_column(db.Float, nullable=False)
    photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="place")


class Photo(db.Model):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    place_id: Mapped[int] = mapped_column(Integer, ForeignKey("places.id"))
    photo_reference: Mapped[str] = mapped_column(String(200), nullable=False)
    place: Mapped["Place"] = relationship("Place", back_populates="photos")

#
#
# with app.app_context():
#     db.create_all()
