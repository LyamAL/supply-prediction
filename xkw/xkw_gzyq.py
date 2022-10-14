import folium
import geopandas
import pandas

from features_construction import toGeoFence
from site_covid_visual import random_color
from warehouse_type_addr import drawByCities


def yq1():
    site_early_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/疫情场景数据/site_control_type_04160517.csv',
        engine='python',
        skip_blank_lines=True)
    site_late_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/疫情场景数据/site_control_type_05250809.csv',
        engine='python',
        skip_blank_lines=True)
    site_all_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv',
        engine='python',
        skip_blank_lines=True)

    df2 = pandas.read_excel(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/sites.xlsx')
    ls = list(df2.columns)
    site_early_df = site_early_df[~site_early_df['node_name'].isin(ls)]
    site_late_df = site_late_df[~site_late_df['node_name'].isin(ls)]
    site_covid_df = pandas.concat([site_early_df, site_late_df])
    site_covid_df.to_csv('covid_sites_left.csv', index=False, encoding='gbk')

    pass


def yq2():
    map = folium.Map(location=[31.3004, 121.294], zoom_start=10)
    site_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓_gps_营业部_polygon_/上海营业站位置信息with合并围栏.csv',
        engine='python',
        skip_blank_lines=True)
    site_df['fence'] = geopandas.GeoSeries.from_wkt(site_df['fence'])
    site_df = geopandas.GeoDataFrame(site_df, geometry='fence')
    site_df.set_crs(epsg="4326", inplace=True)
    df2 = pandas.read_excel(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/sites.xlsx')
    ls = list(df2.columns)
    site_df = site_df[site_df['node_name'].isin(ls)]

    poly_color = [random_color() for _ in range(site_df.shape[0])]
    site_df['color'] = poly_color
    # 画polygon
    for index, row in site_df.iterrows():
        fillColor = row['color']
        color = 'white'
        polyg_ = folium.GeoJson(
            row['fence'],
            style_function=lambda x, fillColor=fillColor, color=color: {
                "fillColor": fillColor,
                "color": color,
                'weight': 1,
                'fillOpacity': 0.5},
        )
        polyg_.add_to(map)

    map.fit_bounds(map.get_bounds(), padding=(10, 10))

    map.save('xkw/sites.html')


def yq3():
    site_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv',
        engine='python',
        skip_blank_lines=True)
    site_df = toGeoFence(site_df, 'fence')
    site_df['area'] = site_df.apply(lambda x: x['fence'].area, axis=1)
    site_df = site_df[['area', 'site_code']]
    covid_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/site_features_covid.csv',
        engine='python',
        skip_blank_lines=True)
    covid_df = pandas.merge(site_df, covid_df, on='site_code', how='right')
    covid_df.to_csv('site_info.csv', index=False)
    pass


if __name__ == '__main__':
    # yq2()
    yq3()
