import unittest
import os 
import csv

from shapely import Point, MultiPolygon
from datetime import datetime

from cyclone_data import Cyclone, CycloneObservationData
from geography_parsing import get_polygon_from_geojson
from hurdat2_parsing import transform_header_to_cyclone, transform_data_row_to_cod, parse_coord_string, parse_hurdat2_file
from hurricane_report import generate_csv_report

class TestHurricaneCode(unittest.TestCase):

    def test_cyclone_add_observation(self):
        test_cyclone = Cyclone("name", "basin", "cyclone_num", "year", 10)
        test_data = CycloneObservationData(Point(1,1), datetime, "L", 1)
        test_cyclone.add_observation(test_data)
        self.assertEqual(len(test_cyclone.observations), 1)
    
    def test_cyclone_max_wind_speed(self):
        test_cyclone = Cyclone("name", "basin", "cyclone_num", "year", 10)
        test_data_1 = CycloneObservationData(Point(1,1), datetime, "L", 1)
        test_data_2 = CycloneObservationData(Point(1,1), datetime, "L", 3)
        test_data_3 = CycloneObservationData(Point(1,1), datetime, "L", 2)
        test_cyclone.add_observation(test_data_1)
        test_cyclone.add_observation(test_data_2)
        test_cyclone.add_observation(test_data_3)
        self.assertEqual(test_cyclone.get_max_wind_speed(), 3)

    def test_get_polygon_from_geojson(self):
        p = get_polygon_from_geojson(os.path.join(os.getcwd(), "resources", "florida.geojson"))
        self.assertIsInstance(p, MultiPolygon)
    
    def test_transform_header_to_cyclone(self):
        row = ["AL092011","              IRENE","     43", ""]
        cyc = transform_header_to_cyclone(row)
        with self.subTest():
            self.assertEqual(cyc.name, "IRENE")
        with self.subTest():
            self.assertEqual(cyc.basin, "AL")
        with self.subTest():
            self.assertEqual(cyc.cyclone_num, "09")
        with self.subTest():
            self.assertEqual(cyc.year, "2011")
        with self.subTest():
            self.assertEqual(cyc.num_observations, 43)

    def test_transform_data_row_to_cod(self):
        row = ["20110821", "0000", "", "TS", "15.0N", "59.0W", "45", "1006", "105","    0", "0","45","0","0", "0", "0", "0", "0", "0","0", "-999"]
        cod = transform_data_row_to_cod(row)
        with self.subTest():
            self.assertAlmostEqual(cod.location.x, -59.0)
        with self.subTest():
            self.assertAlmostEqual(cod.location.y, 15.0)
        with self.subTest():
            self.assertEqual(cod.datetime.year, 2011)
        with self.subTest():
            self.assertEqual(cod.record_identifier, "")
        with self.subTest():
            self.assertEqual(cod.max_wind, 45)

    def test_parse_coord_string(self):
        coord_1 = "1.0N"
        coord_2 = "22.0W"
        c1_num = parse_coord_string(coord_1)
        c2_num = parse_coord_string(coord_2)
        with self.subTest():
            self.assertAlmostEqual(c1_num, 1.0)
        with self.subTest():
            self.assertAlmostEqual(c2_num, -22.0)

    def test_parse_hurdat2_file(self):
        cyclones = parse_hurdat2_file(os.path.join(os.getcwd(), "resources", "hurdat2_test.csv"))
        with self.subTest():
            self.assertEqual(len(cyclones), 4)
        with self.subTest():
            self.assertEqual(cyclones[0].name, "IRENE")
        with self.subTest():
            self.assertEqual(len(cyclones[0].observations), 1)
        with self.subTest():
            self.assertEqual(len(cyclones[1].observations), 4)

    def test_generate_csv_report(self):
        cyclones = parse_hurdat2_file(os.path.join(os.getcwd(), "resources", "hurdat2_test.csv"))
        polygon = get_polygon_from_geojson(os.path.join(os.getcwd(), "resources", "florida.geojson"))
        generate_csv_report(cyclones, polygon)
        with open("landfall_report.csv") as f:
            reader = csv.reader(f)
            next(reader)
            data = list(reader)
        with self.subTest():
            self.assertEquals(len(data), 3)
        with self.subTest():
            self.assertEquals(data[0][0], "IRENE")
        with self.subTest():
            self.assertEquals(data[1][0], "ALBERTA")
        with self.subTest():
            self.assertEquals(data[2][0], "ALBERTINA")
        os.remove("landfall_report.csv")


if __name__ == '__main__':
    unittest.main()