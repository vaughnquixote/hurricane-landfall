import json
import shapefile

from shapely import from_geojson


def get_polygon_from_geojson(geojson_file):
    
    with open(geojson_file) as file:
        state_borders = json.load(file)
        # for feat in state_borders["features"]:
        #     if feat["properties"]["NAME"] == "Florida":
        #         polygon = from_geojson(json.dumps(feat))
        polygon = from_geojson(json.dumps(state_borders))
    
    return polygon

def get_polygon_from_shapefile(shapefile_name):

    sf = shapefile.Reader(shapefile_name)

    polygon = from_geojson(json.dumps(sf.__geo_interface__))
    print(len(sf.__geo_interface__["features"][0]["geometry"]["coordinates"]))

    return polygon