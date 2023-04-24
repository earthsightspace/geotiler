"""
Define the Place class for working with geometries
"""


from shapely.geometry import mapping, shape, Point
from shapely.ops import transform
from pyproj import Transformer, CRS


class Place:
    """
    A class representing a geographic place with a given geometry and Coordinate Reference System (CRS).

    Attributes:
        input_crs (pyproj.CRS): The input Coordinate Reference System.
        input_geometry (shapely.geometry.base.BaseGeometry): The input geometry as a shapely object.
        wgs_crs (pyproj.CRS): The WGS84 (EPSG:4326) Coordinate Reference System.
        wgs_geometry (shapely.geometry.base.BaseGeometry): The input geometry transformed to WGS84 (EPSG:4326).
    """

    def __init__(self, input_crs, input_geometry):
        """
        Initializes a Place object with an input CRS and geometry.

        Args:
            input_crs (str or pyproj.CRS): The input Coordinate Reference System.
            input_geometry (dict or shapely.geometry.base.BaseGeometry): The input geometry as a GeoJSON dictionary
                or shapely object.
        """
        self.input_crs = CRS(input_crs)
        self.input_geometry = self._to_shapely_geometry(input_geometry)
        self.wgs_geometry = self.transform_to_crs("EPSG:4326")


    def _to_shapely_geometry(self, input_geometry):
        """
        Converts the input geometry to a shapely object if needed.

        Args:
            input_geometry (dict or shapely.geometry.base.BaseGeometry): The input geometry as a GeoJSON dictionary
                or shapely object.

        Returns:
            shapely.geometry.base.BaseGeometry: The input geometry as a shapely object.
        """
        if isinstance(input_geometry, dict):
            return shape(input_geometry)
        else:
            return shape(input_geometry)


    def transform_to_crs(self, target_crs):
        """
        Transforms the input geometry to the specified target CRS.

        Args:
            target_crs (str or pyproj.CRS): The target Coordinate Reference System.

        Returns:
            shapely.geometry.base.BaseGeometry: The input geometry transformed to the target CRS.
        """
        target_crs = CRS(target_crs)
        transformer = Transformer.from_crs(self.input_crs, target_crs, always_xy=True)
        return transform(transformer.transform, self.input_geometry)


    def to_geojson(self):
        """
        Returns a GeoJSON representation of the input geometry.

        Returns:
            dict: A GeoJSON dictionary representing the input geometry.
        """
        return mapping(self.input_geometry)
    
    
    def _utm_epsg_for_point(self, x, y):
        """
        Returns the UTM EPSG code for a given point (x, y).

        Args:
            x (float): Longitude of the point.
            y (float): Latitude of the point.

        Returns:
            int: UTM EPSG code.
        """
        zone_number = int((x + 180) // 6) + 1
        if y < 0:
            epsg_code = 32700 + zone_number  # Southern hemisphere
        else:
            epsg_code = 32600 + zone_number  # Northern hemisphere
        return epsg_code


    def _generate_grid_points(self, resolution=0.1):
        """
        Generate a grid of points within the geometry.

        Args:
            resolution (float): The distance (in WGS degrees) between adjacent points in the grid.

        Returns:
            list: A list of shapely.geometry.Point objects within the geometry.
        """
        minx, miny, maxx, maxy = self.wgs_geometry.bounds
        grid_points = list()

        x = minx
        while x <= maxx:
            y = miny
            while y <= maxy:
                point = Point(x, y)
                if self.wgs_geometry.contains(point):
                    grid_points.append(point)
                y += resolution
            x += resolution

        return grid_points


    def find_intersecting_utm_zones(self, resolution=0.1):
        """
        Finds all intersecting UTM zones for the input geometry.

        Args:
            resolution (float, optional): The distance between adjacent points in the grid.
                Smaller values will result in a more accurate result but slower computation. Defaults to 0.1.

        Returns:
            set: A set of intersecting UTM zones as pyproj.CRS objects.
        """
        grid_points = self._generate_grid_points(resolution)
        intersecting_zones = set()

        for point in grid_points:
            epsg_code = self._utm_epsg_for_point(point.x, point.y)
            intersecting_zones.add(CRS.from_epsg(epsg_code))

        return intersecting_zones

