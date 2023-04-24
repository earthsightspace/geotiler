"""
Unit tests for the Tile class
"""


import unittest

from shapely.geometry import box

from geotiler.tile import Tile


class TestTile(unittest.TestCase):
    def test_tile_creation(self):
        utm_crs = 32633
        utm_start = (500000, 6000000)
        tile_size = (1000, 1000)

        tile = Tile(utm_crs, utm_start, tile_size)

        self.assertEqual(tile.utm_crs, utm_crs)
        self.assertEqual(tile.utm_start, utm_start)
        self.assertEqual(tile.tile_size, tile_size)

        utm_geometry = box(utm_start[0], utm_start[1],
                           utm_start[0] + tile_size[0], utm_start[1] + tile_size[1])

        self.assertTrue(tile.utm_geometry.equals_exact(utm_geometry, tolerance=0.0001))
        self.assertTrue(tile.tile_id.startswith("32633_"))

    def test_tile_from_identifier(self):
        tile_id = "32633_500000_6000000_1000_1000"
        tile = Tile.from_tile_id(tile_id)

        self.assertEqual(tile.utm_crs, 32633)
        self.assertEqual(tile.utm_start, (500000, 6000000))
        self.assertEqual(tile.tile_size, (1000, 1000))

        utm_geometry = box(500000, 6000000, 501000, 6001000)
        self.assertTrue(tile.utm_geometry.equals_exact(utm_geometry, tolerance=0.0001))
        self.assertEqual(tile.tile_id, tile_id)

if __name__ == '__main__':
    unittest.main()
