import os
from data import data
import googlemaps
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for

from db_models import db, Place
from url_modifier import URLModifier

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


def modify_urls(venues, api_key):
    for venue in venues:
        if venue.photo_url:
            photo_url_modifier = URLModifier(venue.photo_url)
            venue.photo_url = photo_url_modifier.modify_param("key", api_key)
            print(venue.photo_url)

        if venue.map_url:
            map_url_modifier = URLModifier(venue.map_url)
            venue.map_url = map_url_modifier.modify_param("key", api_key)
            print(venue.map_url)
    return venues


@app.route("/")
def home():
    result = db.session.execute(db.select(Place))
    venues = result.scalars().all()
    modified_venues = modify_urls(venues, GOOGLE_API_KEY)
    return render_template("index.html", all_venues=modified_venues)


@app.route("/venue/<int:venue_id>", methods=["GET", "POST"])
def venue_details(venue_id):
    requested_venue = db.get_or_404(Place, venue_id)
    modified_venues = modify_urls([requested_venue], GOOGLE_API_KEY)
    modified_venue = modified_venues[0]
    return render_template("venue_details.html", venue=modified_venue)


@app.route("/delete/<int:venue_id>", methods=["GET", "POST"])
def delete_venue(venue_id):
    venue_to_delete = db.get_or_404(Place, venue_id)
    db.session.delete(venue_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


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
            print(place_details)
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


@app.route("/get_static_map", methods=["GET"])
def get_static_map():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    if lat and lng:
        map_location = (
            f"https://maps.googleapis.com/maps/api/staticmap?center={lat},"
            f"{lng}&zoom=15&size=640x640&markers=color:red%7Clabel:%7C{lat},{lng}&key={GOOGLE_API_KEY}"
        )
        return jsonify({"map_image_url": map_location})
    else:
        return jsonify({"error": "Latitude and longitude not provided"}), 400


@app.route("/get_photo_url", methods=["GET"])
def get_photo_url():
    photo_reference = request.args.get("photo_reference")
    max_width = request.args.get("max_width", 640)
    max_height = request.args.get("max_height", 640)
    if photo_reference:
        photo_url = (
            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}"
            f"&maxheight={max_height}&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
        )
        return jsonify({"photo_url": photo_url})
    else:
        return jsonify({"error": "Photo reference not provided"}), 400


@app.route("/add_venue", methods=["GET", "POST"])
def add_venue():
    if request.method == "POST":
        place_id = request.form.get("place_id")
        name = request.form.get("name")
        address = request.form.get("address")
        lat = request.form.get("lat")
        lng = request.form.get("lng")
        rating = request.form.get("rating")
        photo_url = request.form.get("photo_url")
        map_url = request.form.get("static_map_url")

        photo_url_modifier = URLModifier(photo_url)
        new_photo_url = photo_url_modifier.remove_param("key")

        map_url_modifier = URLModifier(map_url)
        new_map_url = map_url_modifier.remove_param("key")

        new_place = Place(
            name=name,
            address=address,
            rating=rating,
            place_id=place_id,
            lng=lng,
            lat=lat,
            photo_url=new_photo_url,
            map_url=new_map_url,
        )

        db.session.add(new_place)
        db.session.commit()

        return redirect(url_for("home"))
    return render_template("add_venue.html")


if __name__ == "__main__":
    app.run(debug=True)
