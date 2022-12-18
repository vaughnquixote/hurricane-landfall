import csv

from datetime import datetime
from shapely import Point
from cyclone_data import CycloneObservationData, Cyclone

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

    max_wind_speed = int(row[6].strip())
    return CycloneObservationData(loc, cyclone_datetime, indicator, max_wind_speed)
    
def parse_hurdat2_file(filename):
    
    cyclones = []

    with open(filename) as hurdat_file:
        reader = csv.reader(hurdat_file)

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