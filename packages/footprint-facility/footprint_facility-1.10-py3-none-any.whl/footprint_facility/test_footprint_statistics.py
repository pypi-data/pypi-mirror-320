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
from unittest import TestCase

import folium
import geojson
import shapely
from shapely import wkt
from shapely.geometry import shape

import footprint_facility
from . import set_precision, rework_to_polygon_geometry, AlreadyReworkedPolygon

try:
    from .footprint_statistcs import (compute_area_from_4326,
                                      area_to_user_readable,
                                      FootprintStatistics,
                                      _compute_simplify,
                                      _compute_convex_hull)
except ImportError:
    from footprint_statistcs import (compute_area_from_4326,
                                     area_to_user_readable,
                                     FootprintStatistics,
                                     _compute_simplify,
                                     _compute_convex_hull)


#############################################################################
# Test Class
#############################################################################
class TestStatistics(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_compute_area_from_4326_1(self):
        poly = wkt.loads('''\
            POLYGON ((24.8085317 46.8512821,
                24.7986952 46.8574619,
                24.8088238 46.8664741,
                24.8155239 46.8576335,
                24.8085317 46.8512821))''')

        self.assertAlmostEqual(abs(compute_area_from_4326(poly)), 1083466.869,
                               delta=1e-3)

    def test_compute_area_from_4326_2(self):
        """
        Huge sample area coming form leaflet sample
        """
        poly = wkt.loads('''\
            POLYGON((20 35, 22 34, 45 20, 30 5, 10 10, 10 30, 20 35))''')

        self.assertAlmostEqual(abs(compute_area_from_4326(poly)),
                               7_927_593_710_574.936,
                               delta=1e-3)

    def test_area_to_user_readable(self):
        value = area_to_user_readable(10_000_000)
        self.assertTrue('km<sup>2' in value)
        value = area_to_user_readable(100_000)
        self.assertTrue('m<sup>2' in value)

    def test_class_footprint_statistics(self):
        fp = wkt.loads(
            "POLYGON((20 35, 22 34, 45 20, 30 5, 10 10, 10 30, 20 35))")
        stats = FootprintStatistics(fp, footprint_facility.simplify(
            fp, tolerance=0.5, tolerance_in_meter=False))
        self.assertEqual(stats.origin_points(), 7)
        self.assertEqual(stats.reworked_points(), 6)
        self.assertTrue(isinstance(stats.map(), folium.Map))

    def test_class_simplify_statistics(self):
        fp = shape(
            {
                "coordinates":
                    [
                        [
                            [
                                [3.292, 47.148],
                                [5.651, 46.967],
                                [4.963, 48.912],
                                [1.887, 48.873],
                                [1.137, 46.395],
                                [3.557, 44.765],
                                [3.292, 47.148]
                            ]
                        ],
                        [
                            [
                                [7.195, 47.032],
                                [7.195, 49.461],
                                [5.844, 49.461],
                                [5.844, 47.032],
                                [7.195, 47.032]
                            ]
                        ]
                    ],
                "type": "MultiPolygon"
            })
        stats = _compute_simplify(
            fp, tolerance=10.0, tolerance_in_meter=False)
        self.assertEqual(stats.tolerance, 10.0)
        self.assertEqual(stats.origin_points(), 12)
        self.assertEqual(stats.reworked_points(), 11)
        self.assertTrue(isinstance(stats.map(), folium.Map))

        stats = _compute_convex_hull(fp)
        self.assertEqual(stats.origin_points(), 12)
        self.assertEqual(stats.reworked_points(), 11)
        self.assertTrue(isinstance(stats.map(), folium.Map))

        poly_simple = fp.geoms[0]
        stats = _compute_convex_hull(poly_simple)
        self.assertEqual(stats.origin_points(), 7)
        self.assertEqual(stats.reworked_points(), 6)
        self.assertTrue(isinstance(stats.map(), folium.Map))

    def test_class_simplify_statistics_to_geojson(self):
        fp = shape(
            {
                "coordinates":
                    [
                        [
                            [
                                [3.292, 47.148],
                                [5.651, 46.967],
                                [4.963, 48.912],
                                [1.887, 48.873],
                                [1.137, 46.395],
                                [3.557, 44.765],
                                [3.292, 47.148]
                            ]
                        ],
                        [
                            [
                                [7.195, 47.032],
                                [7.195, 49.461],
                                [5.844, 49.461],
                                [5.844, 47.032],
                                [7.195, 47.032]
                            ]
                        ]
                    ],
                "type": "MultiPolygon"
            })

        stats = _compute_simplify(fp, tolerance=10.0, tolerance_in_meter=False)
        _geojson = stats.to_geojson()
        for feature in _geojson:
            self.assertTrue(geojson.Feature(feature).is_valid)

        stats = _compute_convex_hull(fp)
        _geojson = stats.to_geojson()
        for feature in _geojson:
            self.assertTrue(geojson.Feature(feature).is_valid)

    def test_conversion_coordinates(self):
        _wkt = """POLYGON((75.58244101140099 -85.29943099459616, 66.5853
        -85.0811, 46.7204 -83.1675, 36.0471 -80.8235, 29.6757 -78.3048,
        25.456 -75.7029, 22.4275 -73.0557, 20.1175 -70.3808, 18.2714
        -67.6878, 16.7404 -64.9819, 15.4325 -62.2664, 14.2879 -59.5433,
        13.266 -56.8141, 12.3381 -54.0796, 11.4837 -51.3405, 10.6874
        -48.5973, 9.93764 -45.8504, 9.22526 -43.1001, 8.54317 -40.3466,
        7.88562 -37.5902, 7.24788 -34.831, 6.62603 -32.0692, 6.01674
        -29.305, 5.41711 -26.5387, 4.82464 -23.7704, 4.23706 -21.0002,
        3.65232 -18.2286, 3.0685 -15.4556, 2.48378 -12.6815, 1.89642
        -9.90659, 1.30468 -7.13115, 0.706828 -4.35545, 0.101093 -1.57983,
        -0.51437 1.19541, -1.14151 3.9699, -1.78241 6.74326, -2.43933
        9.51511, -3.11477 12.285, -3.81149 15.0525, -4.53257 17.8171,
        -5.28156 20.5783, -6.06243 23.3354, -6.87981 26.0878, -7.73911
        28.8348, -8.64659 31.5754, -9.60971 34.3089, -10.6373 37.0339,
        -11.7401 39.7492, -12.931 42.4532, -14.2259 45.1438, -15.6443
        47.8187, -17.2107 50.4749, -18.956 53.1084, -20.9197 55.7142,
        -23.1527 58.2859, -25.7211 60.8146, -28.7407 63.3095, -32.2759
        65.7113, -36.5031 68.0184, -41.6199 70.1983, -47.8722 72.2041,
        -55.5302 73.9711, -64.8174 75.4121, -75.7446 76.4234, -87.8992
        76.9054, -100.397 76.7995, -112.195 76.1196, -122.56 74.9431,
        -131.251 73.3747, -138.378 71.514, -144.196 69.4397, -148.97 67.21,
        -152.931 64.8659, -156.259 62.4363, -159.092 59.9417, -161.536
        57.3968, -163.669 54.8122, -165.552 52.1959, -167.231 49.5539,
        -168.743 46.8906, -170.116 44.2097, -171.373 41.5139, -172.531
        38.8056, -173.607 36.0865, -174.611 33.3581, -175.554 30.6218,
        -176.444 27.8785, -177.288 25.1292, -178.092 22.3748, -178.861
        19.6159, -179.6 16.8532, -180 15.299267415730355, -180 90, 180 90,
        180 15.299267415730355, 179.688 14.0872, 178.999 11.3185, 178.33
        8.54753, 177.679 5.77478, 177.043 3.00064, 176.42 0.225521, 175.808
        -2.55022, 175.205 -5.32624, 174.61 -8.10221, 174.019 -10.8778,
        173.433 -13.6528, 172.849 -16.4268, 172.265 -19.1997, 171.679
        -21.9712, 171.09 -24.741, 170.495 -27.5089, 169.893 -30.2748,
        169.279 -33.0384, 168.652 -35.7995, 168.008 -38.558, 167.342
        -41.3137, 166.65 -44.0663, 165.925 -46.8156, 165.16 -49.5614,
        164.345 -52.3034, 163.467 -55.0411, 162.509 -57.7739, 161.447
        -60.5012, 160.25 -63.2219, 158.872 -65.9344, 157.243 -68.6363,
        155.254 -71.3237, 152.729 -73.9903, 149.351 -76.6243, 144.524
        -79.2029, 136.984 -81.6753, 123.827 -83.9119, 100.82387906202558
        -85.42641978721186, 100.8 -85.7265, 100.825 -85.9, 100.702 -85.909,
        90.8040265674998 -85.66880876800023, 75.6155 -85.8996, 75.6882
        -85.7284, 75.58244101140099 -85.29943099459616), (88.11476108761217
        -72.02536107007776, 90.5777 -71.8897, 99.0172 -70.9868, 106.583
        -69.7353, 113.21 -68.1949, 118.942 -66.4222, 123.873 -64.4652,
        128.119 -62.3629, 131.788 -60.1457, 134.979 -57.8371, 137.773
        -55.4553, 140.237 -53.0142, 142.428 -50.5246, 144.388 -47.995,
        146.156 -45.4321, 147.759 -42.841, 149.224 -40.2263, 150.568
        -37.5912, 151.81 -34.9387, 152.962 -32.2711, 154.035 -29.5905,
        155.041 -26.8985, 155.986 -24.1966, 156.878 -21.486, 157.722
        -18.7679, 158.524 -16.0431, 159.289 -13.3126, 160.019 -10.5772,
        160.719 -7.83745, 161.391 -5.09407, 162.038 -2.34762, 162.661
        0.401369, 163.265 3.15242, 163.849 5.90507, 164.415 8.65892, 164.965
        11.4136, 165.501 14.1687, 166.022 16.924, 166.531 19.6791, 167.028
        22.4339, 167.514 25.1879, 167.989 27.9411, 168.454 30.6933, 168.91
        33.4442, 169.357 36.1937, 169.795 38.9418, 170.224 41.6883, 170.646
        44.4331, 171.058 47.1763, 171.462 49.9177, 171.857 52.6574, 172.242
        55.3954, 172.616 58.1317, 172.977 60.8664, 173.322 63.5996, 173.648
        66.3312, 173.948 69.0614, 174.213 71.7903, 174.423 74.518, 174.547
        77.2444, 174.516 79.9695, 174.157 82.693, 172.888 85.413, 166.781
        88.1169, 20.3724 89.0493, 4.29171 86.3786, 2.25149 83.6613, 1.68051
        80.9387, 1.56185 78.2142, 1.64156 75.4883, 1.82645 72.7612, 2.07425
        70.0328, 2.36316 67.3032, 2.68373 64.5486, 3.02299 61.8161, 3.37891
        59.0822, 3.74844 56.3466, 4.12959 53.6094, 4.521 50.8705, 4.92181
        48.1299, 5.33147 45.3876, 5.74967 42.6435, 6.17631 39.8979, 6.61142
        37.1506, 7.05516 34.4018, 7.5078 31.6517, 7.96971 28.9002, 8.44135
        26.1477, 8.92326 23.3942, 9.41609 20.64, 9.92058 17.8853, 10.4375
        15.1304, 10.968 12.3755, 11.5129 9.62091, 12.0734 6.86705, 12.6511
        4.11426, 13.2472 1.36292, 13.8636 -1.38652, 14.5022 -4.13359,
        15.165 -6.8778, 15.8547 -9.61856, 16.5739 -12.3553, 17.3258
        -15.0873, 18.1142 -17.8139, 18.9432 -20.5341, 19.8177 -23.2472,
        20.7433 -25.952, 21.7265 -28.6474, 22.7752 -31.332, 23.8983
        -34.0041, 25.1067 -36.6619, 26.4133 -39.3032, 27.8333 -41.9253,
        29.3854 -44.5249, 31.0922 -47.0982, 32.9811 -49.64, 35.086 -52.1444,
        37.4483 -54.6035, 40.1192 -57.0075, 43.1618 -59.3436, 46.6526
        -61.5953, 50.6834 -63.7411, 55.3608 -65.7531, 60.7981 -67.5957,
        67.1017 -69.2238, 74.3385 -70.5836, 82.4869 -71.616,
        88.11476108761217 -72.02536107007776))"""

        geometry = wkt.loads(_wkt)
        set_precision(0.01)
        try:
            geometry = rework_to_polygon_geometry(geometry)
        except AlreadyReworkedPolygon:
            pass
        orig_count = shapely.count_coordinates(geometry)
        print(f'Number on point in original: {orig_count}')
        simpled = footprint_facility.simplify(
            geometry, tolerance=10000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 10km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=20000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 20km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=50000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 50km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=100000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 100km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=150000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 150km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=200000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 200km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=500000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 500km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=1000000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 1000km tolerance: {simpled_count}')

    def test_simplify_austria(self):
        _wkt = """POLYGON ((95.0089 -48, 99.4821 -48, 103.955 -48, 108.429
        -48, 112.902 -48, 117.375 -48, 121.848 -48, 126.321 -48, 130.795
        -48, 135.268 -48, 139.741 -48, 144.214 -48, 148.687 -48, 153.161
        -48, 157.634 -48, 162.107 -48, 166.58 -48, 171.054 -48, 175.527 -48,
        179.991 -48, 179.991 -47.8393, 179.991 -47.3839, 179.991 -46.9286,
        179.991 -46.4732, 179.991 -46.0179, 179.991 -45.5625, 179.991
        -45.1071, 179.991 -44.6518, 179.991 -44.1964, 179.991 -43.7411,
        179.991 -43.2857, 179.991 -42.8304, 179.991 -42.375, 179.991
        -41.9196, 179.991 -41.4643, 179.991 -41.0089, 179.991 -40.5536,
        179.991 -40.0982, 179.991 -39.6429, 179.991 -39.1875, 179.991
        -38.7321, 179.991 -38.2768, 179.991 -37.8214, 179.991 -37.3661,
        179.991 -36.9107, 179.991 -36.4554, 179.991 -36, 179.991 -35.5446,
        179.991 -35.0893, 179.991 -34.6339, 179.991 -34.1786, 179.991
        -33.7232, 179.991 -33.2679, 179.991 -32.8125, 179.991 -32.3571,
        179.991 -31.9018, 179.991 -31.4464, 179.991 -30.9911, 179.991
        -30.5357, 179.991 -30.0804, 179.991 -29.625, 179.991 -29.1696,
        179.991 -28.7143, 179.991 -28.2589, 179.991 -27.8036, 179.991
        -27.3482, 179.991 -26.8929, 179.991 -26.4375, 179.991 -25.9821,
        179.991 -25.5268, 179.991 -25.0714, 179.991 -24.6161, 179.991
        -24.1607, 179.991 -23.7054, 179.991 -23.25, 179.991 -22.7946,
        179.991 -22.3393, 179.991 -21.8839, 179.991 -21.4286, 179.991
        -20.9732, 179.991 -20.5179, 179.991 -20.0625, 179.991 -19.6071,
        179.991 -19.1518, 179.991 -18.6964, 179.991 -18.2411, 179.991
        -17.7857, 179.991 -17.3304, 179.991 -16.875, 179.991 -16.4196,
        179.991 -15.9643, 179.991 -15.5089, 179.991 -15.0536, 179.991
        -14.5982, 179.991 -14.1429, 179.991 -13.6875, 179.991 -13.2321,
        179.991 -12.7768, 179.991 -12.3214, 179.991 -11.8661, 179.991
        -11.4107, 179.991 -10.9554, 179.991 -10.5, 179.991 -10.0446, 179.991
        -9.58929, 179.991 -9.13393, 179.991 -8.67857, 179.991 -8.22321,
        179.991 -7.76786, 179.991 -7.3125, 179.991 -6.85714, 179.991
        -6.40179, 179.991 -5.94643, 179.991 -5.49107, 179.991 -5.03571,
        179.991 -4.58036, 179.991 -4.125, 179.991 -3.66964, 179.991
        -3.21429, 179.991 -2.75893, 179.991 -2.30357, 179.991 -1.84821,
        179.991 -1.39286, 179.991 -0.9375, 179.991 -0.482143, 179.991
        -0.0267857, 179.991 0.428571, 179.991 0.883929, 179.991 1.33929,
        179.991 1.79464, 179.991 2.25, 179.991 2.70536, 179.991 3.16071,
        179.991 3.61607, 179.991 4.07143, 179.991 4.52679, 179.991 4.98214,
        179.991 5.4375, 179.991 5.89286, 179.991 6.34821, 179.991 6.80357,
        179.991 7.25893, 179.991 7.71429, 179.991 8.16964, 179.991 8.625,
        179.991 9.08036, 179.991 9.53571, 179.991 9.99107, 175.527 9.99107,
        171.054 9.99107, 166.58 9.99107, 162.107 9.99107, 157.634 9.99107,
        153.161 9.99107, 148.687 9.99107, 144.214 9.99107, 139.741 9.99107,
        135.268 9.99107, 130.795 9.99107, 126.321 9.99107, 121.848 9.99107,
        117.375 9.99107, 112.902 9.99107, 108.429 9.99107, 103.955 9.99107,
        99.4821 9.99107, 95.0089 9.99107, 95.0089 9.53571, 95.0089 9.08036,
        95.0089 8.625, 95.0089 8.16964, 95.0089 7.71429, 95.0089 7.25893,
        95.0089 6.80357, 95.0089 6.34821, 95.0089 5.89286, 95.0089 5.4375,
        95.0089 4.98214, 95.0089 4.52679, 95.0089 4.07143, 95.0089 3.61607,
        95.0089 3.16071, 95.0089 2.70536, 95.0089 2.25, 95.0089 1.79464,
        95.0089 1.33929, 95.0089 0.883929, 95.0089 0.428571, 95.0089
        -0.0267857, 95.0089 -0.482143, 95.0089 -0.9375, 95.0089 -1.39286,
        95.0089 -1.84821, 95.0089 -2.30357, 95.0089 -2.75893, 95.0089
        -3.21429, 95.0089 -3.66964, 95.0089 -4.125, 95.0089 -4.58036,
        95.0089 -5.03571, 95.0089 -5.49107, 95.0089 -5.94643, 95.0089
        -6.40179, 95.0089 -6.85714, 95.0089 -7.3125, 95.0089 -7.76786,
        95.0089 -8.22321, 95.0089 -8.67857, 95.0089 -9.13393, 95.0089
        -9.58929, 95.0089 -10.0446, 95.0089 -10.5, 95.0089 -10.9554, 95.0089
        -11.4107, 95.0089 -11.8661, 95.0089 -12.3214, 95.0089 -12.7768,
        95.0089 -13.2321, 95.0089 -13.6875, 95.0089 -14.1429, 95.0089
        -14.5982, 95.0089 -15.0536, 95.0089 -15.5089, 95.0089 -15.9643,
        95.0089 -16.4196, 95.0089 -16.875, 95.0089 -17.3304, 95.0089
        -17.7857, 95.0089 -18.2411, 95.0089 -18.6964, 95.0089 -19.1518,
        95.0089 -19.6071, 95.0089 -20.0625, 95.0089 -20.5179, 95.0089
        -20.9732, 95.0089 -21.4286, 95.0089 -21.8839, 95.0089 -22.3393,
        95.0089 -22.7946, 95.0089 -23.25, 95.0089 -23.7054, 95.0089
        -24.1607, 95.0089 -24.6161, 95.0089 -25.0714, 95.0089 -25.5268,
        95.0089 -25.9821, 95.0089 -26.4375, 95.0089 -26.8929, 95.0089
        -27.3482, 95.0089 -27.8036, 95.0089 -28.2589, 95.0089 -28.7143,
        95.0089 -29.1696, 95.0089 -29.625, 95.0089 -30.0804, 95.0089
        -30.5357, 95.0089 -30.9911, 95.0089 -31.4464, 95.0089 -31.9018,
        95.0089 -32.3571, 95.0089 -32.8125, 95.0089 -33.2679, 95.0089
        -33.7232, 95.0089 -34.1786, 95.0089 -34.6339, 95.0089 -35.0893,
        95.0089 -35.5446, 95.0089 -36, 95.0089 -36.4554, 95.0089 -36.9107,
        95.0089 -37.3661, 95.0089 -37.8214, 95.0089 -38.2768, 95.0089
        -38.7321, 95.0089 -39.1875, 95.0089 -39.6429, 95.0089 -40.0982,
        95.0089 -40.5536, 95.0089 -41.0089, 95.0089 -41.4643, 95.0089
        -41.9196, 95.0089 -42.375, 95.0089 -42.8304, 95.0089 -43.2857,
        95.0089 -43.7411, 95.0089 -44.1964, 95.0089 -44.6518, 95.0089
        -45.1071, 95.0089 -45.5625, 95.0089 -46.0179, 95.0089 -46.4732,
        95.0089 -46.9286, 95.0089 -47.3839, 95.0089 -47.8393, 95.0089 -48))"""
        geometry = wkt.loads(_wkt)
        set_precision(0.01)
        try:
            geometry = rework_to_polygon_geometry(geometry)
        except AlreadyReworkedPolygon:
            pass
        orig_count = shapely.count_coordinates(geometry)
        print(f'Number on point in original: {orig_count}')
        simpled = footprint_facility.simplify(
            geometry, tolerance=1, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 1m tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=100, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 100m tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=500, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 500m tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=1000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 1km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=10000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 10km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=100000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 100km tolerance: {simpled_count}')

        simpled = footprint_facility.simplify(
            geometry, tolerance=500000, tolerance_in_meter=True)
        simpled_count = shapely.count_coordinates(simpled)
        print(f'Simplified with 500km tolerance: {simpled_count}')
