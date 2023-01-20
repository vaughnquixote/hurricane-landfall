import csv
import sys
import os

from hurdat2_parsing import parse_hurdat2_file
from geography_parsing import get_polygon_from_geojson

def format_datetime(datetime):
    """
    Accept a python datetime object and return a formatted string with
    the date in MM/DD/YYYY format. 

    Params:
    datetime (datetime.datetime): python datetime object

    Return:
    formatted_date (str): string in MM/DD/YYYY format
    """
    formatted_date = f"{datetime.month}/{datetime.day}/{datetime.year}"
    return formatted_date

def generate_csv_report(cyclones, polygon, \
    output_filename="landfall_report.csv"):
    """
    Generate and save a CSV report file indicating the name, date and maximum 
    wind speed for each hurricane from the provided data which made landfall 
    in a provided polygon. The report will contain the date of first landfall.

    Params:
    cyclones (list[Cyclone]): a list of cyclone objects as defined in 
        cyclone_data.py
    polygon (shapely.Polygon or shapely.MultiPolygon): a polygon representing
        the state/geographical boundary

    Returns:
    None
    """

    with open(output_filename, "w") as reportfile:
        reportwriter = csv.writer(reportfile)
        reportwriter.writerow(["name", "date", "max_wind_speed"])
        # check each cyclone in the provided data
        for cyc in cyclones:
            # check each data record for the cyclone
            for obs in cyc.observations:
                # if the center of the storm is in the polygon, add a a record
                # to the report file
                if polygon.contains(obs.location):
                    date = format_datetime(obs.datetime)
                    reportwriter.writerow([cyc.name, date,\
                        cyc.get_max_wind_speed()])
                    break

def identify_landfall_in_polygon(cyclone_list, polygon):
    """
    Utility used during development to generate summary stats based on the 
    input data and the polygon.
    """
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

def process_cyclone_data(hurdat2_file, geojson_file, output_dir=""):
    """
    Accepts a hurdat2 filename and a geojson filename, parses the files and 
    then generates a csv report based on the data.

    HURDAT2 format specification provided by NOAA, more info here:
    https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf

    Params:
    hurdat2_file (str): filename/path for a file in HURDAT2 format
    geojson_file (str): filename/path for a file in geojson format inteded to
        represent a state boundary
    """
    if output_dir == "":
        output_dir = os.getcwd()
        
    try:
        cyclones = []
    
        cyclones = parse_hurdat2_file(hurdat2_file)

        florida = get_polygon_from_geojson(geojson_file)
    
        generate_csv_report(cyclones, florida, \
            output_filename=os.path.join(output_dir, "landfall_report.csv"))
    except Exception as e:
        print("Processing failed with message:")
        print(str(e))
        return False
    return True

def main():
    hurdat2_file = sys.argv[1]
    geojson_file = sys.argv[2]
    process_cyclone_data(hurdat2_file, geojson_file)

if __name__ == "__main__":
    main()