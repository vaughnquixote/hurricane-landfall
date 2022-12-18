import csv
import json
import sys

from shapely import Point
from shapely import from_geojson
from datetime import datetime


class Cyclone:

    def __init__(self, name, basin, cyclone_num, year, num_observations):
        self.name = name
        self.basin = basin
        self.cyclone_num = cyclone_num
        self.year = year
        self.locations = []
        self.landfall = False
        self.num_observations = num_observations
        self.observations = []

    def add_observation(self, observation_data):
        self.observations.append(observation_data)

    def add_location(self, latitude, longitude):
        new_loc = Point(longitude, latitude)
        self.locations.append(new_loc)

class CycloneObservationData:

    def __init__(self, location, datetime, record_identifier, max_wind):
        self.location = location
        self.datetime = datetime
        self.record_identifier = record_identifier
        self.max_wind = max_wind

def transform_header_to_cyclone(row):
    basin = row[0][:2]
    cyclone_num = row[0][2:4]
    year = row[0][4:]
    name = row[1].strip()
    num_observations = int(row[2].strip()) 
    return Cyclone(name, basin, cyclone_num, year, num_observations)

def parse_coord_string(coordinate):
    cardinal_dir = coordinate[-1]
    coordinate = coordinate[:-1]
    numeric_coordinate = float(coordinate)
    if cardinal_dir == "S" or cardinal_dir == "W":
        numeric_coordinate *= -1
    return numeric_coordinate

def transform_data_row_to_cod(row):
    year = int(row[0][:4])
    month = int(row[0][4:6])
    day = int(row[0][6:])
    time = row[1].strip()
    hours = int(time[:2])
    minutes = int(time[2:])
    cyclone_datetime = datetime(year, month, day, hours, minutes)

    indicator = row[2].strip()
    lat_str = row[4].strip()
    lon_str = row[5].strip()
    lat_parsed = parse_coord_string(lat_str)
    lon_parsed = parse_coord_string(lon_str)
    loc = Point(lon_parsed, lat_parsed)

    max_wind_speed = row[6].strip()
    return CycloneObservationData(loc, cyclone_datetime, indicator, max_wind_speed)
    
def parse_hurdat2_file(filename):
    
    cyclones = []
    irregular_data = []

    with open(filename) as hurdat_file:
        reader = csv.reader(hurdat_file)
        curr_cyclone = None

        for row in reader:
            if len(row) == 4:
                curr_cyclone = transform_header_to_cyclone(row)
                cyclones.append(curr_cyclone)
            elif len(row) == 21:
                cyc_observation = transform_data_row_to_cod(row)
                curr_cyclone.add_observation(cyc_observation)
                if cyc_observation.record_identifier == "L":
                    curr_cyclone.landfall = True
    
    return cyclones

def get_polygon_from_geojson(geojson_file):
    
    with open(geojson_file) as file:
        state_borders = json.load(file)
        for feat in state_borders["features"]:
            if feat["properties"]["NAME"] == "Florida":
                florida_polygon = from_geojson(json.dumps(feat))
    
    return florida_polygon

def identify_landfall_in_polygon(cyclone_list, polygon):
    num_landfall_verified = 0
    num_landfall_fl = 0
    no_landfall = 0
    landfall_indicator_and_not_identified = 0
    no_ind_ided = 0

    for cyc in cyclone_list:
        has_landfall = False
        for obs in cyc.observations:
            if polygon.contains(obs.location):
                has_landfall = True
                break

        if has_landfall:
            num_landfall_fl += 1
        if not (has_landfall or cyc.landfall):
            no_landfall += 1
        if has_landfall and cyc.landfall:
            num_landfall_verified += 1
        if not has_landfall and cyc.landfall:
            landfall_indicator_and_not_identified += 1
        if has_landfall and not cyc.landfall:
            no_ind_ided += 1
    
    return num_landfall_fl, no_landfall, num_landfall_verified, landfall_indicator_and_not_identified, no_ind_ided

def process_cyclone_data(hurdat2_file, geojson_file):
    cyclones = []
    
    cyclones = parse_hurdat2_file(hurdat2_file)

    print(f"processed {len(cyclones)} hurricanes")

    florida = get_polygon_from_geojson(geojson_file)

    num_landfall, no_landfall, verified, missed, potential_bad_data = identify_landfall_in_polygon(cyclones, florida)
    
    print(f"identified landfall in florida: {num_landfall}")
    print(f"verified landfall: {verified}")
    print(f"verified no landfall: {no_landfall}")
    print(f"missed landfall: {missed}")
    print(f"identified and no indicator: {potential_bad_data}")
    print(f"total categorized: {verified + no_landfall + missed + potential_bad_data}")

def main():
    hurdat2_file = sys.argv[1]
    geojson_file = sys.argv[2]
    process_cyclone_data(hurdat2_file, geojson_file)

if __name__ == "__main__":
    main()