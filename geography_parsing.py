import json

from shapely import from_geojson

def get_polygon_from_geojson(geojson_file):
    
    with open(geojson_file) as file:
        state_borders = json.load(file)
        for feat in state_borders["features"]:
            if feat["properties"]["NAME"] == "Florida":
                florida_polygon = from_geojson(json.dumps(feat))
    
    return florida_polygon