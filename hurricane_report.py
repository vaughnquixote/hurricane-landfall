import csv
import sys

from hurdat2_parsing import parse_hurdat2_file
from geography_parsing import get_polygon_from_geojson


def generate_csv_report(cyclones, polygon):
    with open('fl_landfall_report.csv', 'w') as reportfile:
        reportwriter = csv.writer(reportfile)
        reportwriter.writerow(['name', 'date', 'max_wind_speed'])
        for cyc in cyclones:
            for obs in cyc.observations:
                if polygon.contains(obs.location):
                    date = f"{obs.datetime.month}/{obs.datetime.day}/{obs.datetime.year}"
                    reportwriter.writerow([cyc.name, date, cyc.get_max_wind_speed()])
                    break


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
    
    generate_csv_report(cyclones, florida)

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