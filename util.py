import math
import operator
import re
import time
import random

from shapely.geometry import MultiPolygon
import geopy.distance
import pandas
from shapely.affinity import affine_transform
from shapely.geometry import Point
from shapely.ops import triangulate
import requests as requests
from shapely import wkt
from shapely.geometry import mapping


def plotDotforDataframe(point, map):
    import folium
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your this_map'''
    folium.CircleMarker(location=[point.lat, point.lng],
                        radius=1, fillOpacity=0.5,
                        weight=4).add_to(map)


def geocodeB(address):
    """
    @ address: 名称字符串
    @ 返回值：经度，纬度
    """
    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    base_url = "http://api.map.baidu.com/geocoder?address={address}&output=json&key=TaMeTaBAcffNbvUSxEeRarCSpuYgDwQ7" \
        .format(address=address)
    try:
        response = s.get(base_url)
        answer = response.json()
        latitude = answer['result']['location']['lat']
        longitude = answer['result']['location']['lng']
    except Exception:
        time.sleep(1)
        return 0, 0
    return longitude, latitude


x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方


def bd09_to_gcj02(lng, lat):
    x = lng - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def geocodeBDetailed(address):
    """
    @ address: 名称字符串
    @ 返回值：经度，纬度
    """
    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    base_url = "http://api.map.baidu.com/geocoder?ret_coordtype=gcj02II&address={address}&output=json&key=TaMeTaBAcffNbvUSxEeRarCSpuYgDwQ7" \
        .format(address=address)
    try:
        response = s.get(base_url)
        answer = response.json()
        latitude = answer['result']['location']['lat']
        longitude = answer['result']['location']['lng']
    except Exception:
        time.sleep(1)
        return 0, 0
    return gcj02_to_wgs84(longitude, latitude)


def degeocodeBDetailed(lat, lng):
    """
    @ address: 名称字符串
    @ 返回值：经度，纬度
    """
    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    base_url = "http://api.map.baidu.com/reverse_geocoding/v3/?coordtype=wgs84ll&output=json&ak=TaMeTaBAcffNbvUSxEeRarCSpuYgDwQ7&location={lat},{lng}" \
        .format(lat=lat, lng=lng)
    try:
        response = s.get(base_url)
        answer = response.json()
        province = answer['result']['addressComponent']['province']
        city = answer['result']['addressComponent']['city']
    except Exception:
        time.sleep(1)
        return '', ''
    return province, city


def extract(p):
    poly_mapped = mapping(p)
    poly_coordinates = poly_mapped['coordinates'][0]
    poly_x = [coords[0] for coords in poly_coordinates]
    poly_y = [coords[1] for coords in poly_coordinates]
    return len(poly_x), poly_x, poly_y


def pnpoly(testx, testy, polygon):
    nvert, vertx, verty = extract(polygon)
    c = 0
    for i in range(0, nvert):
        if i == 0:
            j = nvert - 1
        else:
            j = i - 1
        if operator.ne(operator.gt(verty[i], testy), operator.gt(verty[j], testy)) and \
                operator.lt(testx, (vertx[j] - vertx[i]) * (verty[i]) / (verty[j] - verty[i]) + vertx[i]):
            c = 1 - c  # 点在多变形内
    return c


def pnpolyShaple(polygon, point):
    # polygon = shapely.wkt.loads('POLYGON ((51.0 3.0, 51.3 3.61, 51.3 3.0, 51.0 3.0))')#
    # point = shapely.geometry.Point(x,y)#float to point
    return polygon.contains(point)


from numpy import concatenate

link = lambda a, b: concatenate((a, b[1:]))
edge = lambda a, b: concatenate(([a], [b]))


def qhull2D(sample):
    import sys, threading
    sys.setrecursionlimit(10 ** 7)  # max depth of recursion
    threading.stack_size(2 ** 27)  # new thread will get stack of such size
    from numpy import dot, repeat, argmax, take, argmin
    def dome(sample, base):
        h, t = base
        dists = dot(sample - h, dot(((0, -1), (1, 0)), (t - h)))
        outer = repeat(sample, dists > 0, 0)
        if len(outer):
            pivot = sample[argmax(dists)]
            return link(dome(outer, edge(h, pivot)),
                        dome(outer, edge(pivot, t)))
        else:
            return base

    if len(sample) > 2:
        axis = sample[:, 0]
        base = take(sample, [argmin(axis), argmax(axis)], 0)
        return link(dome(sample, base), dome(sample, base[::-1]))
    else:
        return sample


def minBoundingRect(hull_points_2d):
    from numpy import nanmin, dot, transpose, unique, zeros, array, nanmax
    import sys
    edges = zeros((len(hull_points_2d) - 1, 2))  # empty 2 column array
    for i in range(len(edges)):
        edge_x = hull_points_2d[i + 1, 0] - hull_points_2d[i, 0]
        edge_y = hull_points_2d[i + 1, 1] - hull_points_2d[i, 1]
        edges[i] = [edge_x, edge_y]
    edge_angles = zeros((len(edges)))  # empty 1 column array
    for i in range(len(edge_angles)):
        edge_angles[i] = math.atan2(edges[i, 1], edges[i, 0])
    for i in range(len(edge_angles)):
        edge_angles[i] = abs(edge_angles[i] % (math.pi / 2))  # want strictly positive answers
    edge_angles = unique(edge_angles)
    min_bbox = (0, sys.maxsize, 0, 0, 0, 0, 0, 0)  # rot_angle, area, width, height, min_x, max_x, min_y, max_y
    for i in range(len(edge_angles)):
        R = array([[math.cos(edge_angles[i]), math.cos(edge_angles[i] - (math.pi / 2))],
                   [math.cos(edge_angles[i] + (math.pi / 2)), math.cos(edge_angles[i])]])
        rot_points = dot(R, transpose(hull_points_2d))  # 2x2 * 2xn
        min_x = nanmin(rot_points[0], axis=0)
        max_x = nanmax(rot_points[0], axis=0)
        min_y = nanmin(rot_points[1], axis=0)
        max_y = nanmax(rot_points[1], axis=0)
        width = max_x - min_x
        height = max_y - min_y
        area = width * height
        if (area < min_bbox[1]):
            min_bbox = (edge_angles[i], area, width, height, min_x, max_x, min_y, max_y)
    angle = min_bbox[0]
    R = array([[math.cos(angle), math.cos(angle - (math.pi / 2))], [math.cos(angle + (math.pi / 2)), math.cos(angle)]])
    proj_points = dot(R, transpose(hull_points_2d))  # 2x2 * 2xn
    min_x = min_bbox[4]
    max_x = min_bbox[5]
    min_y = min_bbox[6]
    max_y = min_bbox[7]
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_point = dot([center_x, center_y], R)
    # Calculate corner points and project onto rotated frame
    corner_points = zeros((4, 2))  # empty 2 column array
    corner_points[0] = dot([max_x, min_y], R)
    corner_points[1] = dot([min_x, min_y], R)
    corner_points[2] = dot([min_x, max_y], R)
    corner_points[3] = dot([max_x, max_y], R)

    # rot_angle, area, width, height, center_point, corner_points
    return (angle, min_bbox[1], min_bbox[2], min_bbox[3], center_point,
            corner_points)


# 凸边形质心
def centroid(vertexes):
    _x_list = [vertex[0] for vertex in vertexes]
    _y_list = [vertex[1] for vertex in vertexes]
    _len = len(vertexes)
    _x = sum(_x_list) / _len
    _y = sum(_y_list) / _len
    return (_x, _y)


def countLockDown(s):
    if pandas.isna(s):
        return 0, 0, 0
    return len(re.findall('封', s)), len(re.findall('管', s)), len(re.findall('[防未]', s))


def random_points_in_polygon(polygon, k):
    "Return list of k points chosen uniformly at random inside the polygon."
    areas = []
    transforms = []
    for t in triangulate(polygon):
        areas.append(t.area)
        (x0, y0), (x1, y1), (x2, y2), _ = t.exterior.coords
        transforms.append([x1 - x0, x2 - x0, y2 - y0, y1 - y0, x0, y0])
    points = []
    for transform in random.choices(transforms, weights=areas, k=k):
        x, y = [random.random() for _ in range(2)]
        if x + y > 1:
            p = Point(1 - x, 1 - y)
        else:
            p = Point(x, y)
        points.append(affine_transform(p, transform))
    if k == 1:
        return points[0].x, points[0].y
    return points


# 凸边形质心
def centroidShapely(polygon):
    p1 = wkt.loads(str(polygon))
    point = wkt.loads(p1.centroid.wkt)
    return point.x, point.y


def toMultiPolygonShapely(p):
    MultiPolygon([wkt.loads(p)])
    pass


def distance(coords_1, coords_2):
    if isinstance(coords_2, Point):
        coords_1 = coords_1.coords
        coords_2 = coords_2.coords
    return geopy.distance.distance(coords_1, coords_2).km


#
# def distance(x1, y1, x2, y2):
#     return geopy.distance.distance((y1, x1), (y2, x2)).km

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

