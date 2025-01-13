from __future__ import annotations

import msgspec
# from typing import Union

Coordinates = list[float, float]

class Point:
    coordinates = Coordinates

class MultiPoint:
    coordinates: list[Coordinates]

class LineString:
    coordinates: list[Coordinates]

class MultiLineString:
    coordinates: list[list[Coordinates]]

class Polygon:
    coordinates: list[list[Coordinates]]

class MultiPolygon:
    coordinates: list[list[list[Coordinates]]]

class GeometryCollection:
    geometries: list[Geometry]


Geometry = (
    Point
    | MultiPoint
    | LineString
    | MultiLineString
    | Polygon
    | MultiPolygon
    | GeometryCollection
)

# Define the two Feature types
class Feature:
    geometry: Geometry | None = None
    properties: dict | None = None
    id: str | int | None = None

class FeatureCollection:
    features: list[Feature]


# A union of all 9 GeoJSON types
GeoJSON = Geometry | Feature | FeatureCollection

# Create a decoder and an encoder to use for decoding & encoding GeoJSON types
loads = msgspec.json.Decoder(GeoJSON).decode
dumps = msgspec.json.Encoder().encode
