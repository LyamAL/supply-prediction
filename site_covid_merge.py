import datetime
import pandas
import geopandas

import util
from features_construction import toGeoFence

if __name__ == '__main__':
    site_df = pandas.read_csv('/Users/lyam/同步空间/数据/疫情场景数据/site_with_covid_info_v3.csv',
                              engine='python',
                              skip_blank_lines=True)
    covid_df = pandas.read_csv('/Users/lyam/同步空间/数据/疫情数据/covid_with_jd_gps.csv', engine='python',
                               skip_blank_lines=True)
    site_df = toGeoFence(site_df, 'fence')

    site_covid_df = pandas.DataFrame(
        columns=['site_code', 'node_name', 'dt', 'lockdown_count', 'safe_count', 'restraint_count'])

    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date

    covid_df['dt'] = pandas.to_datetime(covid_df['dt'], format='%Y/%m/%d')
    covid_df = covid_df[
        ['id', 'city', 'control_type', 'county', 'town', 'subdivision', 'dt', 'lng', 'lat']]
    covid_df.sort_values(
        ascending=True, inplace=True, by=['dt'])

    while cur_date <= end_date:  # 获得疫情数据
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

    site_covid_df.to_csv('/Users/lyam/同步空间/数据/疫情场景数据/site_control_type_04160517.csv', index=False)
