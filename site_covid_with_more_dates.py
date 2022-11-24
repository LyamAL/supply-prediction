import pandas
import datetime

from shapely import geometry

import util
from features_construction import toGeoFence


def formatAddress(x):
    if x['addr'][0:2] == '上海':
        return x['addr'] + x['name']
    if x['name'][0:2] == '上海':
        return x['name'] + x['addr']
    return x['city_name'] + x['area_name'] + x['addr']


if __name__ == '__main__':
    # covid_df = pandas.read_csv('/Users/lyam/同步空间/数据/疫情数据/最新上海疫情数据_20220921190302.csv',
    #                            engine='python', skip_blank_lines=True,
    #                            parse_dates=['date'])
    # covid_df['x'] = covid_df['x'].apply(lambda x: x / 1e7)
    # covid_df['y'] = covid_df['y'].apply(lambda x: x / 1e7)
    # # covid_df = covid_df[covid_df['epidemic_level'] != '未知']
    # covid_gps_df = covid_df.drop_duplicates(subset=['x', 'y'])
    # covid_gps_df = covid_gps_df[['name', 'addr', 'x', 'y', 'city_name', 'area_name']]
    # covid_gps_df['address'] = covid_gps_df.apply(lambda x: formatAddress(x), axis=1)
    # covid_gps_df[['lng', 'lat']] = covid_gps_df.apply(
    #     lambda x: util.geocodeBDetailed(x['address']),
    #     axis=1,
    #     result_type='expand')
    # covid_gps_df = covid_gps_df[['x', 'y', 'lng', 'lat']]
    # covid_df = pandas.merge(covid_df, covid_gps_df, on=['x', 'y'], how='left')
    #
    # covid_df['date'] = covid_df['date'].apply(
    #     lambda x: x.replace(hour=0, minute=0, second=0))
    # covid_df = covid_df[['epidemic_level', 'area_name', 'date', 'lng', 'lat', 'addr']]
    # covid_df.drop_duplicates(inplace=True)
    # covid_df.sort_values(ascending=True, inplace=True, by=['date'])
    # covid_df['id'] = range(len(covid_df))
    # covid_df.index = covid_df['id']
    # covid_df.to_csv('covid_0608.csv', index=False)
    site_df = pandas.read_csv('/Users/lyam/同步空间/数据/营业站/site_revised_gps_v2.csv',
                              engine='python',
                              skip_blank_lines=True)
    covid_df = pandas.read_csv('covid_0608.csv',
                               engine='python', parse_dates=['date'],
                               skip_blank_lines=True)
    site_df = toGeoFence(site_df, 'fence')
    site_df.sort_values(ascending=True, inplace=True, by=['county_name'])
    site_df.index = site_df['site_code']
    districts = list(site_df['county_name'].unique())

    start_date = datetime.datetime(2022, 5, 25, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 8, 9, hour=23, minute=0, second=0)
    cur_date = start_date
    while cur_date <= end_date:
        md = cur_date.strftime("%m-%d")
        site_df[md] = None
        tomorrow = (cur_date + datetime.timedelta(days=1))
        covid_df_i = covid_df[(covid_df['date'] >= cur_date) & (covid_df['date'] < tomorrow)]
        cur_date += datetime.timedelta(days=1)
        covid_df_i.sort_values(ascending=True, inplace=True, by=['area_name'])
        for county in districts:
            covid_df_i_county = covid_df_i[covid_df_i['area_name'] == county]
            if covid_df_i_county.shape[0] == 0:
                continue
            site_df_county = site_df[site_df['county_name'] == county]
            site_df_county.index = site_df_county['site_code']
            for index, row in site_df_county.iterrows():
                isEmpty = True
                for i, r in covid_df_i_county.iterrows():
                    if util.pnpolyShaple(row['fence'], geometry.Point(r['lng'], r['lat'])):
                        # 点在多边形内
                        if isEmpty:
                            site_df.at[index, md] = str(r['id']) + '-' + r['epidemic_level'] + ";"
                            isEmpty = False
                        else:
                            site_df.at[index, md] += str(r['id']) + '-' + r['epidemic_level'] + ";"

    site_covid_df = pandas.DataFrame(
        columns=['site_code', 'node_name', 'dt', 'lockdown_count', 'safe_count', 'restraint_count'])
    cur_date = start_date

    while cur_date <= end_date:
        md = cur_date.strftime("%m-%d")
        cur_date += datetime.timedelta(days=1)
        site_df_daily = site_df[
            ['site_code', 'node_name', 'county_name', 'lng',
             'lat', 'fence',
             md]]
        site_df_daily[['lockdown_count', 'restraint_count', 'safe_count']] = site_df_daily.apply(
            lambda x: util.countLockDown(x[md]), axis=1,
            result_type='expand')
        for index, row in site_df_daily.iterrows():
            data = {'site_code': row['site_code'], 'node_name': row['node_name'], 'dt': cur_date,
                    'lockdown_count': row['lockdown_count'], 'restraint_count': row['restraint_count'],
                    'safe_count': row['safe_count'],
                    }
            site_covid_df = pandas.concat([site_covid_df, pandas.DataFrame.from_records([data])])

    site_covid_df.to_csv('/Users/lyam/同步空间/数据/疫情场景数据/site_control_type_05250809.csv', index=False)
    exit(0)
