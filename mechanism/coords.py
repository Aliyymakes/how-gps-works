"""Turn latitude, longitude and sky directions into x, y, z points on a sphere.

The origin is the centre of the Earth. The x axis points to latitude 0, longitude 0.
The y axis points to latitude 0, longitude 90 east. The z axis points to the north pole.
"""

import math

from mechanism.constants import EARTH_RADIUS_M, GPS_ORBIT_RADIUS_M


def _point(x_m, y_m, z_m):
    return {"x_m": float(x_m), "y_m": float(y_m), "z_m": float(z_m)}


def latlon_to_xyz(lat_deg, lon_deg, height_m=0):
    """Return the point at this latitude, longitude and height above the sphere."""
    if not -90 <= lat_deg <= 90:
        return {"error": "Latitude must be between -90 and 90 degrees."}
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    # Distance from the centre of the Earth.
    radius = EARTH_RADIUS_M + height_m
    # cos(lat) is the share of the radius that lies in the flat equator plane.
    x_m = radius * math.cos(lat) * math.cos(lon)
    y_m = radius * math.cos(lat) * math.sin(lon)
    # Height up the pole axis only depends on latitude.
    z_m = radius * math.sin(lat)
    return _point(x_m, y_m, z_m)


def xyz_to_latlon(x_m, y_m, z_m):
    """Return latitude, longitude and height above the sphere for a point."""
    # Distance from the centre of the Earth.
    radius = math.sqrt(x_m**2 + y_m**2 + z_m**2)
    if radius == 0:
        return {"error": "The centre of the Earth has no latitude or longitude."}
    # Latitude is the angle above the equator plane.
    flat = math.sqrt(x_m**2 + y_m**2)
    lat_deg = math.degrees(math.atan2(z_m, flat))
    # Longitude is the angle around the pole axis, measured from the x axis.
    lon_deg = math.degrees(math.atan2(y_m, x_m))
    return {
        "lat_deg": float(lat_deg),
        "lon_deg": float(lon_deg),
        "height_m": float(radius - EARTH_RADIUS_M),
    }


def _local_directions(lat_deg, lon_deg):
    """Unit vectors (east, north, up) at a spot on the ground, each as (x, y, z)."""
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    # Up points straight away from the centre of the Earth.
    up = (math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))
    # East points the way longitude grows; it has no z part.
    east = (-math.sin(lon), math.cos(lon), 0.0)
    # North is at right angles to both: it points toward the pole along the ground.
    north = (-math.sin(lat) * math.cos(lon), -math.sin(lat) * math.sin(lon), math.cos(lat))
    return east, north, up


def satellite_from_sky(receiver_lat_deg, receiver_lon_deg, azimuth_deg, elevation_deg):
    """Return the point at GPS orbit height seen in this direction from the receiver."""
    if not -90 <= receiver_lat_deg <= 90:
        return {"error": "Latitude must be between -90 and 90 degrees."}
    if not 0 <= elevation_deg <= 90:
        return {"error": "Elevation must be between 0 and 90 degrees."}
    receiver = latlon_to_xyz(receiver_lat_deg, receiver_lon_deg)
    east, north, up = _local_directions(receiver_lat_deg, receiver_lon_deg)
    az = math.radians(azimuth_deg)
    el = math.radians(elevation_deg)
    # Sky direction: along the ground (east/north mix) scaled by cos(el), plus up scaled by sin(el).
    ground = [math.sin(az) * e + math.cos(az) * n for e, n in zip(east, north)]
    direction = [math.cos(el) * g + math.sin(el) * u for g, u in zip(ground, up)]
    # Walk t metres along the line so that |receiver + t*direction| = orbit radius.
    # With a = |direction|^2 = 1 this is t^2 + 2*b*t + c = 0.
    start = (receiver["x_m"], receiver["y_m"], receiver["z_m"])
    b = sum(s * d for s, d in zip(start, direction))
    c = sum(s * s for s in start) - GPS_ORBIT_RADIUS_M**2
    # c is negative (the receiver is inside the orbit), so the positive root is the one ahead of us.
    t = -b + math.sqrt(b * b - c)
    return _point(*(s + t * d for s, d in zip(start, direction)))
