"""
   Copyright 2024 - Gael Systems

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import argparse
import os.path
from dataclasses import dataclass

import folium
import geopandas as gpd
import shapely
from geopandas.array import GeometryArray
from shapely import Geometry, wkt
from shapely.geometry import shape, MultiPolygon
import geojson
from pyproj import Geod

import footprint_facility
import logging

logger = logging.getLogger('footprint_statistics')


def compute_area_from_4326(geometry):
    """
    Shapely don't care about the unity used in polygons. EPSG:4326 polygons
    coordinates are in decimal degrees values whereas the area shall be
    expressed in meter. The simplest and most accurate method to manage the
    geographic to geodesic coordinates is to use pyproj library to map
    the polygon on a geoid (i.e. WGS84)
    :param geometry:
    :return:
    """
    geod = Geod(ellps="WGS84")
    if isinstance(geometry, GeometryArray):
        area = 0
        for geo in geometry:
            area += compute_area_from_4326(geo)
    else:
        area = abs(geod.geometry_area_perimeter(geometry)[0])
    return area


def area_to_user_readable(area: float) -> str:
    if area > 1e6:
        return '%.2f km<sup>2' % (area / 1e6)
    else:
        return '%.2f m<sup>2' % area


@dataclass
class FootprintStatistics:
    origin_footprint: Geometry
    reworked_footprint: Geometry
    tolerance: float = None

    def origin_points(self):
        return len(shapely.get_coordinates(self.origin_footprint))

    def reworked_points(self):
        return len(shapely.get_coordinates(self.reworked_footprint))

    def _compute_data_frames(self):
        """
        Performs the geometric comparison ot this statistics inputs.
        The computation uses GeoPanda.
        :return: the set of GeoPanda geometries, ordered as followed:
             1. input origin_footprint
             2. input optimized_footprint,
             3. footprint showing the added part by the optimization
             4. footprint showing the removed part by the optimization
        """
        area = compute_area_from_4326(self.origin_footprint)
        d1 = {'name': ['Origin'],
              'point no': [self.origin_points()],
              'area_in_m': [area],
              'area': [area_to_user_readable(area)],
              'geometry': [self.origin_footprint]}
        area = compute_area_from_4326(self.reworked_footprint)
        d2 = {'name': ['Optimized'],
              'point no': [self.reworked_points()],
              'area_in_m': [area],
              'area': [area_to_user_readable(area)],
              'geometry': [self.reworked_footprint]}
        if self.tolerance:
            d2['tolerance'] = [self.tolerance]

        gdf1 = gpd.GeoDataFrame(d1, crs='epsg:4326')
        gdf2 = gpd.GeoDataFrame(d2, crs='epsg:4326')

        added = gpd.overlay(gdf2, gdf1, how='difference')
        if len(added.count_geometries()) > 0:
            area = compute_area_from_4326(added.geometry.values)
            clean_added = {'name': ['Added Part'],
                           'area_in_m': [area],
                           'area': [area_to_user_readable(area)],
                           'geometry': added.geometry}
            added = gpd.GeoDataFrame(clean_added, crs='epsg:4326')

        removed = gpd.overlay(gdf1, gdf2, how='difference')
        if len(removed.count_geometries()) > 0:
            area = compute_area_from_4326(removed.geometry.values)
            clean_removed = {'name': ['Removed Part'],
                             'area_in_m': [area],
                             'area': [area_to_user_readable(area)],
                             'geometry': removed.geometry}
            removed = gpd.GeoDataFrame(clean_removed, crs='epsg:4326')

        return gdf1, gdf2, added, removed

    def map(self):
        """
        Generates follium/leaflet map to display the results
        :return: the follium map that can be save into html
        """
        origin, optimized, added, removed = self._compute_data_frames()

        m = origin.explore(color='green', tooltip=True,
                           name="Origin Footprint")
        optimized.explore(m=m, color='blue', name='Reworked Footprint')

        added.explore(m=m, color='black', name='Added Part',
                      tooltip=['name', 'area'])
        removed.explore(m=m, color='black', name='Removed Part',
                        tooltip=['name', 'area'])
        folium.LayerControl().add_to(m)  # use folium to add layer control
        return m

    def to_geojson(self) -> geojson:
        # Map the results
        features = []
        for footprint in self._compute_data_frames():
            if footprint.empty:
                continue
            geometry_dict = geojson.loads(footprint.to_json())
            features.extend(geometry_dict['features'])

        statistics = geojson.FeatureCollection(features)
        return statistics


def _compare_footprints(
        geometry1: Geometry, geometry2: Geometry) -> FootprintStatistics:
    stats = FootprintStatistics(geometry1, geometry2)
    try:
        stats.difference = shapely.difference(geometry1, geometry2)
    except Exception as e:
        logger.error('Cannot compute footprints difference', e)
    return stats


def _compute_simplify(
        geometry: Geometry, tolerance: float,
        tolerance_in_meter: bool) -> FootprintStatistics:
    """
    Compute the simplification of the passed geometry and set the tolerance
    statistic info.
    :param geometry: geometry to simplify
    :param tolerance: the expected tolerance
    """
    simplified_geometry = footprint_facility.simplify(
        geometry, tolerance, tolerance_in_meter=tolerance_in_meter)
    stats = _compare_footprints(geometry, simplified_geometry)
    stats.tolerance = tolerance
    return stats


def _compute_convex_hull(geometry: Geometry) -> FootprintStatistics:
    """
    Compute the convex hull of the passed geometry and statistic info.
    :param geometry: geometry to simplify
    """
    if isinstance(geometry, shapely.geometry.MultiPolygon):
        hull = []
        for geo in geometry.geoms:
            hull.append(geo.convex_hull)
        simplified_geometry = MultiPolygon(hull)
    else:
        simplified_geometry = getattr(geometry, 'convex_hull')

    return _compare_footprints(geometry, simplified_geometry)


def main_stats():  # pragma: no cover
    main_parser = argparse.ArgumentParser(
        description='compare footprint optimization results')
    main_parser.add_argument(
        '-v', action='version', help='show the library version and exit',
        version=f'%(prog)s {footprint_facility.__version__}')
    main_parser.add_argument(
        '-f', metavar='orig_footprint', required=True,
        help='the footprint to be optimized')
    main_parser.add_argument(
        '-ff', default='wkt', choices=['wkt', 'geojson'],
        help='passed footprint format (default=wkt)')
    main_parser.add_argument(
        '-o', metavar='output', default='output.html',
        help='output file name of the results. The output format is selected '
             'according to the file extension, if ".htm." HTML interactive '
             'map is generated, otherwise results are returned '
             'in GeoJSON format')
    main_parser.add_argument(
        '-r', action='store_true',
        help='rework the footprint before optimization')
    main_parser.add_argument(
        '-p', metavar='precision', type=float,
        help='defines the optimized/reworked footprint precision '
             '(default=0 no precision defined).')
    main_parser.add_argument(
        '-a', default='simplify', choices=['simplify', 'convex_hull'],
        help='selection of the footprint simplification algorithm')
    main_parser.add_argument(
        '-t', metavar='tolerance', type=float,
        help='the simplify tolerance value')
    main_parser.add_argument(
        '-m', action='store_true',
        help='the tolerance unit is in meter. Overwise no unit conversion '
             'is performed from the geometry input (usually degrees)')

    args = main_parser.parse_args()
    if args.ff == 'wkt':
        orig_footprint = wkt.loads(args.f)
    elif args.ff == 'geojson':
        orig_footprint = shape(geojson.loads(args.f))
    else:
        raise ValueError("Bad footprint format parameter")

    if args.p:
        footprint_facility.set_precision(args.p)

    if args.r:
        orig_footprint = footprint_facility.rework_to_polygon_geometry(
            orig_footprint)
    if args.m:
        tolerance_in_meter = True
    else:
        tolerance_in_meter = False

    filename, extension = os.path.splitext(args.o)
    if not extension:
        extension = '.html'
    output_file = filename + extension

    if args.a == 'simplify':
        if args.t:
            logger.debug(f'selected simplify with tolerance {args.t}')
            stats = _compute_simplify(orig_footprint,
                                      tolerance=args.t,
                                      tolerance_in_meter=tolerance_in_meter)
            if output_file.lower().endswith('.html'):
                stats.map().save(output_file)
            else:
                json = stats.to_geojson()
                with open(output_file, 'w') as fp:
                    geojson.dump(json, fp)

        else:
            raise main_parser.error(
                "Tolerance parameter is missing (please use -t <value>).")
    elif args.a == 'convex_hull':
        logger.debug('selected convex_hull')
        stats = _compute_convex_hull(orig_footprint)
        stats.map().save(output_file)
    else:
        raise main_parser.error(f"Unknown algorithm '{args.a}'")


if __name__ == '__main__':  # pragma: no cover
    main_stats()
