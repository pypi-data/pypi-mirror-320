

def validate_lat_lng(lat: float, lng: float):
    """Validate latitude and longitude values."""
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise ValueError("Latitude must be between -90 and 90, and longitude must be between -180 and 180.")
    
    if not (49.9 <= lat <= 60.9 and -8.2 <= lng <= 1.8):
        raise ValueError("Coordinates must be within the bounds of the UK.")


def validate_polygon(poly: str):
    """Validate polygon string."""
    if not isinstance(poly, str) or not poly:
        raise ValueError("Polygon must be a non-empty string.")

    # Validate format: lat,lng:lat,lng:...
    pairs = poly.split(":")
    for pair in pairs:
        lat_lng = pair.split(",")
        if len(lat_lng) != 2:
            raise ValueError(f"Invalid lat/lng pair: {pair}")
        try:
            lat, lng = map(float, lat_lng)
            validate_lat_lng(lat, lng)  # Ensure valid lat/lng values
        except ValueError:
            raise ValueError(f"Invalid lat/lng values in pair: {pair}")
