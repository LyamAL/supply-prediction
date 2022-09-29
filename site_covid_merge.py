import datetime
import pandas
import geopandas
if __name__ == '__main__':
    site_df = pandas.read_csv('/Users/lyam/Documents/mystuff/idea/数据/营业站/site_covid_jd_gps_宽型md_04160517.csv',
                              engine='python',
                              skip_blank_lines=True)
    covid_df = pandas.read_csv('/Users/lyam/Documents/mystuff/idea/数据/疫情/covid_with_jd_gps.csv', engine='python',
                               skip_blank_lines=True)
    site_covid_df = pandas.DataFrame(
        columns=['site_code', 'node_name', 'dt', 'lockdown_count', 'safe_count', 'restraint_count'])

    site_df['fence'] = geopandas.GeoSeries.from_wkt(site_df['fence'])
    site_df = geopandas.GeoDataFrame(site_df, geometry='fence')
    site_df.set_crs(epsg="4326", inplace=True)

    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date

    covid_df['dt'] = pandas.to_datetime(covid_df['dt'], format='%Y/%m/%d')
    covid_df = covid_df[
        ['id', 'city', 'control_type', 'county', 'town', 'subdivision', 'dt', 'lng', 'lat']]
    covid_df.sort_values(
        ascending=True, inplace=True, by=['dt'])

    # 揪出错误的gps，采用中心点法或随即取点法重新定位gps
    site_df['in_poly'] = site_df.apply(lambda x: pnpoly(x['lng'], x['lat'], x['fence']), axis=1)
    site_df[['lng', 'lat']] = site_df.apply(
        lambda x: (x['lng'], x['lat']) if x['in_poly'] else centroidShapely(x['fence']), axis=1, result_type='expand')
    site_df['in_poly_again'] = site_df.apply(lambda x: pnpoly(x['lng'], x['lat'], x['fence']), axis=1)  # 109
    site_df[['lng', 'lat']] = site_df.apply(
        lambda x: (x['lng'], x['lat']) if x['in_poly_again'] else random_points_in_polygon(x['fence'], 1), axis=1,
        result_type='expand')
    count = site_df['in_poly_again'].value_counts().size
    times = 0
    while count > 1 and times < 20:
        times += 1
        site_df[['lng', 'lat']] = site_df.apply(
            lambda x: (x['lng'], x['lat']) if x['in_poly_again'] else random_points_in_polygon(x['fence'], 1), axis=1,
            result_type='expand')
        site_df['in_poly_again'] = site_df.apply(lambda x: pnpoly(x['lng'], x['lat'], x['fence']), axis=1)
        count = site_df['in_poly_again'].value_counts().size

    site_df.drop('in_poly', axis=1, inplace=True)
    site_df.drop('in_poly_again', axis=1, inplace=True)
    site_df.to_csv('/Users/lyam/Documents/mystuff/idea/数据/营业站/site_revised_gps_covid_宽型md_04160517.csv',
                   index=False)
    while cur_date <= end_date:  # 获得疫情数据
        md = cur_date.strftime("%m-%d")
        cur_date += datetime.timedelta(days=1)
        site_df_daily = site_df[
            ['site_code', 'color', 'node_name', 'county_id', 'county_name', 'lng',
             'lat', 'fence',
             md]]
        site_df_daily[['lockdown_count', 'restraint_count', 'safe_count']] = site_df_daily.apply(
            lambda x: countLockDown(x[md]), axis=1,
            result_type='expand')

        for index, row in site_df_daily.iterrows():
            data = {'site_code': row['site_code'], 'node_name': row['node_name'], 'dt': cur_date,
                    'lockdown_count': row['lockdown_count'], 'restraint_count': row['restraint_count'],
                    'safe_count': row['safe_count'],
                    }
            site_covid_df = pandas.concat([site_covid_df, pandas.DataFrame.from_records([data])])

    site_covid_df.to_csv('/Users/lyam/Documents/mystuff/idea/数据/营业站/site_control_type_04160517.csv')
