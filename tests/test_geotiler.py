"""
Unit tests for the GeoTiler class
"""


import glob
import os
import unittest

from shapely.geometry import Polygon

from geotiler.geotiler import GeoTiler
from geotiler.tile import Tile

class TestGeoTiler(unittest.TestCase):

    def setUp(self):
        # feature collection over Santa Fe, NM area
        fc = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "coordinates": [
                                [
                                    [
                                        -106.2316833845116,
                                        35.8671002112948
                                        ],
                                    [
                                        -106.2316833845116,
                                        35.40894114956603
                                        ],
                                    [
                                        -105.7134540973731,
                                        35.40894114956603
                                        ],
                                    [
                                        -105.7134540973731,
                                        35.8671002112948
                                        ],
                                    [
                                        -106.2316833845116,
                                        35.8671002112948
                                        ]
                                    ]
                                ],
                            "type": "Polygon"
                            }
                        }
                    ]
                }

        self.geometry = fc["features"][0]["geometry"]
        self.geotiler = GeoTiler(self.geometry)
        self.tile_size = 10000
        self.stride = 5000

    def test_tiles_list(self):
        tiles = self.geotiler.tiles_list(tile_size=self.tile_size, stride=self.stride)
        self.assertTrue(all(isinstance(tile, Tile) for tile in tiles))

    def test_tiles_generator(self):
        tiles = self.geotiler.tiles_generator(tile_size=self.tile_size, stride=self.stride)
        self.assertTrue(all(isinstance(tile, Tile) for tile in tiles))

    def test_export_tiles(self):
        output_file_geojson = "test_tiles.geojson"
        output_file_shp = "test_tiles.shp"
        output_file_parquet = "test_tiles.parquet"

        self.geotiler.export_tiles(output_file_geojson, file_format="geojson", tile_size=self.tile_size, stride=self.stride)
        self.geotiler.export_tiles(output_file_shp, file_format="shp", tile_size=self.tile_size, stride=self.stride)
        self.geotiler.export_tiles(output_file_parquet, file_format="geoparquet", tile_size=self.tile_size, stride=self.stride)

        self.assertTrue(os.path.exists(output_file_geojson))
        self.assertTrue(os.path.exists(output_file_shp))
        self.assertTrue(os.path.exists(output_file_parquet))

        output_files = glob.glob("test_tiles.*")
        for output_file in output_files:
            os.remove(output_file)

if __name__ == '__main__':
    unittest.main()
