"""
Unit tests for the Place class
"""


import unittest

from shapely.geometry import Point
from pyproj import CRS

from geotiler.place import Place


class TestPlace(unittest.TestCase):
    def test_init(self):
        place = Place("EPSG:4326", Point(0, 0))
        self.assertIsInstance(place.input_crs, CRS)
        self.assertEqual(place.input_crs.to_string(), "EPSG:4326")

    def test_transform_to_crs(self):
        place = Place("EPSG:4326", Point(0, 0))
        transformed_geom = place.transform_to_crs("EPSG:3857")
        self.assertAlmostEqual(transformed_geom.x, 0, places=7)
        self.assertAlmostEqual(transformed_geom.y, 0, places=7)

    def test_to_geojson(self):
        place = Place("EPSG:4326", Point(0, 0))
        geojson = place.to_geojson()
        self.assertEqual(geojson["type"], "Point")
        self.assertEqual(geojson["coordinates"], (0.0, 0.0))

    def test_find_intersecting_utm_zones(self):
        place = Place("EPSG:4326", Point(0, 0))
        intersecting_zones = place.find_intersecting_utm_zones()
        self.assertEqual(len(intersecting_zones), 1)
        self.assertTrue(CRS.from_epsg(32631) in intersecting_zones)


if __name__ == "__main__":
    unittest.main()
