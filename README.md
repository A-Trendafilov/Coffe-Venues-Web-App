# Coffee Places Web App

A web application to discover and share the best coffee spots around. Built with Flask, Google Maps API, and SQLite.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Screenshots](#Screenshots)

## Features

- Search for coffee places using Google Places Autocomplete API
- Display detailed information about each coffee place
- Add new coffee places with photos and map location
- View a gallery of all added coffee places
- Remove coffee places from the gallery

## Installation

### Prerequisites

- Python 3.x
- Flask
- Google Maps API Key

### Clone the Repository

```shell
git clone https://github.com/A-Trendafilov/Coffe-Venues-Web-App.git
cd coffee-places-web-app
```

### Create a Virtual Environment

```shell
python -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`

```

### Install Dependencies

```shell
pip install -r requirements.txt
```

### Set Up Environment Variables

1. Create a .env file in the project root and add your Google Maps API key and a secret key:

```makefile
SECRET_KEY=your_secret_key
GOOGLE_API_KEY=your_google_api_key
```

### Usage

- Navigate to the homepage to see the gallery of coffee places.
- Use the "Add New Venue" button to add a new coffee place.
- Fill in the details by searching for a place, selecting a photo, and viewing the map location.
- Submit the form to add the place to the gallery.

### API Endpoints

`/autocomplete`

Fetch autocomplete suggestions based on user input.

- Method: GET
- Parameters: query (string)

`/get_place_details`

Fetch detailed information about a place.

- Method: GET
- Parameters: place_id (string)

`/get_static_map`

Fetch a static map image for a location.

- Method: GET
- Parameters: lat (float), lng (float)

`/get_photo_url`

Fetch a photo URL for a place photo.

- Method: GET
- Parameters: photo_reference (string), max_width (int, optional), max_height (int, optional)

`/add_venue`

Add a new coffee place to the database.

- Method: POST
- Parameters: `place_id`, `name`, `address`, `lat`, `lng`, `rating`, `photo_url`, `static_map_url`

`/delete/<int:venue_id>`

Delete a coffee place from the database.

- Method: POST

### Screenshots

<img alt="Screenshot 1" src="/screenshots/coffe-venue-1.png"/>

<img alt="Screenshot 2" src="/screenshots/coffe-venue-2.png"/>

<img alt="Screenshot 3" src="/screenshots/coffe-venue-3.png"/>