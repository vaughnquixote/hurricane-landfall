import csv
import json
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

def parse_file():
    hurricanes = []
    
    hurricanes, _ = parse_hurdat2_file('./resources/hurdat2-1851-2021.txt')

    print(f"processed {len(hurricanes)} hurricanes")

    florida = get_polygon_from_geojson('./resources/gz_2010_us_040_00_500k.json')
    

    
    num_correct = 0
    num_incorrect = 0
    for hurr in hurricanes:
        has_landfall = False
        for loc in hurr.locations:
            if florida.contains(loc):
                lat = loc.y
                lon = loc.x
                has_landfall = True
                break
        
        if has_landfall and hurr.landfall:
            num_correct += 1
        elif not (has_landfall or hurr.landfall):
            num_correct += 1
        else:
            num_incorrect += 1
            if has_landfall and not hurr.landfall:
                print(hurr.name, hurr.year, hurr.cyclone_num)
                print(lat, lon)
    
    print(f"correct {num_correct}")
    print(f"incorrect {num_incorrect}")

def main():
    parse_file()

if __name__ == "__main__":
    main()