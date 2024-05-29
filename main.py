import base64
import os

import googlemaps
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response

from db_models import db, Place

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///places.db"
db.init_app(app)
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    result = db.session.execute(db.select(Place))
    venues = result.scalars().all()
    return render_template("index.html", all_venues=venues)


@app.route("/post/<int:venue_id>", methods=["GET", "POST"])
def venue_details(venue_id):
    requested_venue = db.get_or_404(Place, venue_id)
    return render_template("venue_details.html", venue=requested_venue)


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    search = request.args.get("query")
    if search:
        try:
            response = gmaps.places_autocomplete(input_text=search)
            suggestions = [
                {
                    "description": prediction["description"],
                    "place_id": prediction["place_id"],
                }
                for prediction in response
                if "description" in prediction and "place_id" in prediction
            ]
            return jsonify(suggestions)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify([])


@app.route("/get_place_details", methods=["GET"])
def get_place_details():
    place_id = request.args.get("place_id")
    if place_id:
        try:
            place_details = gmaps.place(place_id=place_id)["result"]
            name = place_details["name"]
            address = place_details["formatted_address"]
            lat = place_details["geometry"]["location"]["lat"]
            lng = place_details["geometry"]["location"]["lng"]
            rating = place_details.get("rating", "N/A")

            photos = [
                photo["photo_reference"] for photo in place_details.get("photos", [])
            ]

            return jsonify(
                {
                    "status": "success",
                    "name": name,
                    "address": address,
                    "rating": rating,
                    "photos": photos,
                    "lat": lat,
                    "lng": lng,
                }
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"status": "error", "message": "Place ID not provided."})


@app.route("/get_map", methods=["GET"])
def get_map():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    if lat and lng:
        map_location = (
            f"https://maps.googleapis.com/maps/api/staticmap?center={lat},"
            f"{lng}&zoom=15&size=640x640&markers=color:red%7Clabel:%7C{lat},{lng}&key={GOOGLE_API_KEY}"
        )
        try:
            response = requests.get(map_location)
            if response.status_code == 200:
                map_image_base64 = base64.b64encode(response.content).decode("utf-8")
                return jsonify({"map_image": map_image_base64})
            else:
                return (
                    jsonify(
                        {"error": "Failed to fetch map image from Google Maps API"}
                    ),
                    500,
                )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Latitude and longitude not provided"}), 400


@app.route("/get_photo", methods=["GET"])
def get_photo():
    photo_reference = request.args.get("photo_reference")
    if photo_reference:
        try:
            response = requests.get(
                f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
            )
            if response.status_code == 200:
                return Response(
                    response.content, content_type=response.headers["Content-Type"]
                )
            else:
                return (
                    jsonify({"error": "Failed to fetch photo from Google Maps API"}),
                    500,
                )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Photo reference not provided"}), 400


@app.route("/get_photo_url", methods=["GET"])
def get_photo_url():
    photo_reference = request.args.get("photo_reference")
    if photo_reference:
        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
        return jsonify({"photo_url": photo_url})
    else:
        return jsonify({"error": "Photo reference not provided"}), 400


@app.route("/add_place", methods=["GET", "POST"])
def add_place():
    if request.method == "POST":
        place_id = request.form.get("place_id")
        name = request.form.get("name")
        address = request.form.get("address")
        lat = request.form.get("lat")
        lng = request.form.get("lng")
        rating = request.form.get("rating")
        photo_reference = request.form.get("photo_reference")

        new_place = Place(
            name=name,
            address=address,
            rating=rating,
            place_id=place_id,
            lng=lng,
            lat=lat,
            photo_reference=photo_reference,
        )

        db.session.add(new_place)
        db.session.commit()

        return redirect(url_for("home"))
    return render_template("add_place.html")


if __name__ == "__main__":
    app.run(debug=True)
