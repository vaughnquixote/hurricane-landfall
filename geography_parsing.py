import json
import shapefile

from shapely import from_geojson


def get_polygon_from_geojson(geojson_file):
    """
    Read a geojson file, meant to represent a state/geographic boundary into
    a Shapely MultiPolygon object.

    Params:
    geojson_file (str): the filename/path of a geojson file to parse

    Returns:
    polygon (shapely.MultiPolygon): a mulitpolygon representation of the 
        state's boundary
    """
    with open(geojson_file) as file:
        state_borders = json.load(file)
        polygon = from_geojson(json.dumps(state_borders))
    
    return polygon

def get_polygon_from_shapefile(shapefile_name):
    """
    Read a shapefile and return a shapely polygon
    """

    sf = shapefile.Reader(shapefile_name)

    polygon = from_geojson(json.dumps(sf.__geo_interface__))

    return polygon