"""
Class definition for a Tile
"""

from shapely.geometry import box
from pyproj import Transformer


class Tile:
    """
    A class that represents a tile in UTM space.

    Attributes:
        utm_crs (pyproj.CRS): The CRS that represents the UTM zone of the tile.
        utm_start (tuple): The starting location in UTM space as a tuple (x, y).
        tile_size (tuple): The size of the tile in UTM space as a tuple (width, height).
        utm_geometry (shapely.geometry.Polygon): The geometry of the tile in UTM space.
        wgs_geometry (shapely.geometry.Polygon): The geometry of the tile in WGS84 space.
        tile_id (str): A unique string identifier for the tile.
    """

    def __init__(self, utm_crs, utm_start, tile_size):
        """
        Initialize the Tile object.

        Args:
            utm_crs (pyproj.CRS): The CRS that represents the UTM zone of the tile.
            utm_start (tuple): The starting location in UTM space as a tuple (x, y).
            tile_size (tuple): The size of the tile in UTM space as a tuple (width, height).
        """
        self.utm_crs = utm_crs
        self.utm_start = utm_start
        self.tile_size = tile_size

        # Create the UTM geometry
        self.utm_geometry = box(utm_start[0], utm_start[1], utm_start[0] + tile_size[0], utm_start[1] + tile_size[1])

        # Create the WGS geometry
        transformer = Transformer.from_crs(utm_crs, CRS.from_epsg(4326), always_xy=True)
        self.wgs_geometry = transformer.transform_geometry(self.utm_geometry)

        # Create a unique string identifier for the tile
        self.tile_id = f"{utm_crs.to_epsg()}_{utm_start[0]}_{utm_start[1]}_{tile_size[0]}_{tile_size[1]}"

    @classmethod
    def from_tile_id(cls, identifier):
        """
        Initialize the Tile object from a tile identifier string.

        Args:
            tile_id (str): The unique tile identifier string.

        Returns:
            Tile: A Tile object corresponding to the identifier.
        """
        # Coerce parameters from the identifier
        epsg_code, x_start, y_start, width, height = map(float, identifier.split('_'))
        utm_crs = CRS.from_epsg(int(epsg_code))
        utm_start = (x_start, y_start)
        tile_size = (width, height)

        return cls(utm_crs, utm_start, tile_size)

    def __repr__(self):
        return f"Tile(identifier={self.identifier}, utm_crs={self.utm_crs}, utm_start={self.utm_start}, tile_size={self.tile_size})"
