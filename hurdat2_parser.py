import csv
import json
import sys
from shapely import Point
from shapely import from_geojson

class Hurricane:

    def __init__(self, name, basin, cyclone_num, year):
        self.name = name
        self.basin = basin
        self.cyclone_num = cyclone_num
        self.year = year
        self.locations = []
        self.landfall = False

    def add_location(self, latitude, longitude):
        new_loc = Point(longitude, latitude)
        self.locations.append(new_loc)

def parse_header(row):
    basin = row[0][:2]
    cyclone_num = row[0][2:4]
    year = row[0][4:]
    name = row[1].strip()
    return Hurricane(name, basin, cyclone_num, year)

def parse_coord_string(coordinate):
    cardinal_dir = coordinate[-1]
    coordinate = coordinate[:-1]
    numeric_coordinate = float(coordinate)
    if cardinal_dir == "S" or cardinal_dir == "W":
        numeric_coordinate *= -1
    return numeric_coordinate

def parse_data_row(row):
    indicator = row[2].strip()
    lat = row[4].strip()
    lon = row[5].strip()
    lat = parse_coord_string(lat)
    lon = parse_coord_string(lon)
    return indicator, lat, lon
    
def parse_hurdat2_file(filename):
    
    hurricanes = []
    irregular_data = []

    with open(filename) as hurdat_file:
        reader = csv.reader(hurdat_file)
        current_hurricane = None

        for row in reader:
            if len(row) == 4:
                current_hurricane = parse_header(row)
                hurricanes.append(current_hurricane)
            elif len(row) == 21:
                indicator, lat, lon = parse_data_row(row)
                current_hurricane.add_location(lat, lon)
                if indicator == "L":
                    current_hurricane.landfall = True
            else:
                irregular_data.append(row)
    
    return hurricanes, irregular_data

def get_polygon_from_geojson(geojson_file):
    
    with open(geojson_file) as file:
        state_borders = json.load(file)
        for feat in state_borders["features"]:
            if feat["properties"]["NAME"] == "Florida":
                florida_polygon = from_geojson(json.dumps(feat))
    
    return florida_polygon

def identify_landfall_in_polygon(hurricane_list, polygon):
    num_landfall_verified = 0
    num_landfall_fl = 0
    no_landfall = 0
    landfall_indicator_and_not_identified = 0
    no_ind_ided = 0

    for hurr in hurricane_list:
        has_landfall = False
        for loc in hurr.locations:
            if polygon.contains(loc):
                lat = loc.y
                lon = loc.x
                has_landfall = True
                break

        if has_landfall:
            num_landfall_fl += 1
        if not (has_landfall or hurr.landfall):
            no_landfall += 1
        if has_landfall and hurr.landfall:
            num_landfall_verified += 1
        if not has_landfall and hurr.landfall:
            landfall_indicator_and_not_identified += 1
        if has_landfall and not hurr.landfall:
            no_ind_ided += 1
    
    return num_landfall_fl, no_landfall, num_landfall_verified, landfall_indicator_and_not_identified, no_ind_ided

def process_hurricane_data(hurdat2_file, geojson_file):
    hurricanes = []
    
    hurricanes, _ = parse_hurdat2_file(hurdat2_file)

    print(f"processed {len(hurricanes)} hurricanes")

    florida = get_polygon_from_geojson(geojson_file)

    num_landfall, no_landfall, verified, missed, potential_bad_data = identify_landfall_in_polygon(hurricanes, florida)
    
    print(f"identified landfall in florida: {num_landfall}")
    print(f"verified landfall: {verified}")
    print(f"verified no landfall: {no_landfall}")
    print(f"missed landfall: {missed}")
    print(f"identified and no indicator: {potential_bad_data}")
    print(f"total categorized: {verified + no_landfall + missed + potential_bad_data}")

def main():
    hurdat2_file = sys.argv[1]
    geojson_file = sys.argv[2]
    process_hurricane_data(hurdat2_file, geojson_file)

if __name__ == "__main__":
    main()