"""
This module contains the GeoTiler class, which is used to generate UTM tiles for a given geometry.
"""


from pathlib import Path

import geopandas as gpd
from tqdm import tqdm

from geotiler.place import Place
from geotiler.tile import Tile


class GeoTiler:
    """
    The GeoTiler class is used to generate UTM tiles for a given geometry.

    Attributes:
        place (Place): The Place object that contains the input geometry.
    """
    
    def __init__(self, geometry, input_crs=4326):
        """
        Initialize the GeoTiler object.

        Args:
            geometry (shapely.geometry.base.BaseGeometry): The input geometry.
            input_crs (int, optional): The input CRS for the geometry. Defaults to 4326 (WGS84).
        """
        self.place = Place(geometry, input_crs)


    def tiles_list(self, tile_size=1000, stride=1000):
        """
        Generate UTM tiles for the input geometry and return a list of Tile objects.

        Args:
            tile_size (int, optional): The size of the tiles in UTM space in both X and Y directions. Defaults to 1000.
            stride (int, optional): The distance between the starting locations of adjacent tiles. Defaults to 1000.

        Returns:
            list: A list of Tile objects that cover the input geometry.
        """
        return list(self.tiles_generator(tile_size, stride))


    def tiles_gdf(self, tile_size=1000, stride=1000):
        """
        Generate UTM tiles for the input geometry and return a GeoDataFrame containing the Tile objects.

        Args:
            tile_size (int, optional): The size of the tiles in UTM space in both X and Y directions. Defaults to 1000.
            stride (int, optional): The distance between the starting locations of adjacent tiles. Defaults to 1000.

        Returns:
            geopandas.GeoDataFrame: A GeoDataFrame containing the Tile objects that cover the input geometry.
        """
        tiles = list(self.tiles_generator(tile_size, stride))
        gdf = gpd.GeoDataFrame(
            {"tile_id": [tile.tile_id for tile in tiles],
            "geometry": [tile.wgs_geometry for tile in tiles],
        })
        gdf.set_crs("EPSG:4326", inplace=True)
        return gdf

    
    def tiles_generator(self, tile_size=1000, stride=1000):
        """
        Generate UTM tiles for the input geometry and return a generator that yields Tile objects.

        Args:
            tile_size (int, optional): The size of the tiles in UTM space in both X and Y directions. Defaults to 1000.
            stride (int, optional): The distance between the starting locations of adjacent tiles. Defaults to 1000.

        Yields:
            Tile: A Tile object that covers part of the input geometry.
        """
        intersecting_zones = self.place.find_intersecting_utm_zones()
        
        progress_bar = tqdm(desc="Generating tiles", ncols=80)

        for utm_crs in intersecting_zones:
            utm_geometry = self.place.transform_to_crs(utm_crs)

            minx, miny, maxx, maxy = utm_geometry.bounds
            x_start = minx - (minx % tile_size)
            y_start = miny - (miny % tile_size)

            x = x_start
            while x < maxx:
                y = y_start
                while y < maxy:
                    tile = Tile(utm_crs, (x, y), (tile_size, tile_size))
                    if utm_geometry.intersects(tile.utm_geometry):
                        yield tile
                        progress_bar.update(1)

                    y += stride
                x += stride

        progress_bar.close()

    
    def export_tiles(self, output_file, file_format="geojson", tile_size=1000, stride=1000):
        """
        Export the list of Tile objects as a GeoJSON, Shapefile, or GeoParquet file.

        Args:
            output_file (str): The path to the output file.
            file_format (str, optional): The format of the output file. Must be one of "geojson", "shp", or "geoparquet". Defaults to "geojson".
            tile_size (int, optional): The size of the tiles in UTM space in both X and Y directions. Defaults to 1000.
            stride (int, optional): The distance between the starting locations of adjacent tiles. Defaults to 1000.
        """
        if file_format not in ["geojson", "shp", "geoparquet"]:
            raise ValueError("Invalid file format. Must be one of 'geojson', 'shp', or 'geoparquet'.")

        tiles = self.tiles_list(tile_size, stride)
        gdf = gpd.GeoDataFrame(
            {"tile_id": [tile.tile_id for tile in tiles],
            "geometry": [tile.wgs_geometry for tile in tiles],
        })
        gdf.set_crs("EPSG:4326", inplace=True)

        output_file = Path(output_file)

        if file_format == "geojson":
            gdf.to_file(output_file, driver="GeoJSON")
        elif file_format == "shp":
            gdf.to_file(output_file.with_suffix(".shp"), driver="ESRI Shapefile")
        elif file_format == "geoparquet":
            gdf.to_parquet(output_file)



