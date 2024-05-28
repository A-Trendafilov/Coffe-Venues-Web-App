import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from dotenv import load_dotenv
import googlemaps

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///places.db"
Bootstrap5(app)

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)


#
# class Place(db.Model):
#     __tablename__ = "places"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     address: Mapped[str] = mapped_column(String(200), nullable=False)
#     place_id: Mapped[str] = mapped_column(String(50), nullable=False)
#     lat: Mapped[float] = mapped_column(db.Float, nullable=False)
#     lng: Mapped[float] = mapped_column(db.Float, nullable=False)
#     photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="place")
#
#
# class Photo(db.Model):
#     __tablename__ = "photos"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     place_id: Mapped[int] = mapped_column(Integer, ForeignKey("places.id"))
#     photo_reference: Mapped[str] = mapped_column(String(200), nullable=False)
#     place: Mapped["Place"] = relationship("Place", back_populates="photos")
#
#
# with app.app_context():
#     db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    search = request.args.get("query")
    if search:
        try:
            response = gmaps.places_autocomplete(input_text=search)
            suggestions = []
            for prediction in response:
                if "description" in prediction and "place_id" in prediction:
                    suggestions.append(
                        {
                            "description": prediction["description"],
                            "place_id": prediction["place_id"],
                        }
                    )
            return jsonify(suggestions)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify([])


@app.route("/get_place_details", methods=["GET"])
def get_place_details():
    place_id = request.args.get("place_id")
    if place_id:
        place_details = gmaps.place(place_id=place_id)["result"]
        name = place_details["name"]
        address = place_details["formatted_address"]
        lat = place_details["geometry"]["location"]["lat"]
        lng = place_details["geometry"]["location"]["lng"]
        rating = place_details.get("rating", "N/A")

        photos = []
        if "photos" in place_details:
            for photo in place_details["photos"]:
                photo_reference = photo["photo_reference"]
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
                photos.append(photo_url)

        map_location = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom=15&size=400x300&markers=color:red%7Clabel:%7C{lat},{lng}&key={GOOGLE_API_KEY}"

        return jsonify(
            {
                "status": "success",
                "name": name,
                "address": address,
                "rating": rating,
                "photos": photos,
                "map_location": map_location,
            }
        )
    return jsonify({"status": "error", "message": "Place ID not provided."})


@app.route("/add_place", methods=["GET", "POST"])
def add_place():
    if request.method == "POST":
        place_id = request.form.get("place_id")
        if place_id:
            place_details = gmaps.place(place_id=place_id)["result"]
            name = place_details["name"]
            address = place_details["formatted_address"]
            lat = place_details["geometry"]["location"]["lat"]
            lng = place_details["geometry"]["location"]["lng"]

            # Create a new Place object
            new_place = Place(
                name=name, address=address, place_id=place_id, lat=lat, lng=lng
            )

            # Add the new place to the database
            db.session.add(new_place)
            db.session.commit()

            return redirect(url_for("home"))  # Redirect to home page after adding place

    return render_template("add_place.html")


if __name__ == "__main__":
    app.run(debug=True)
