import geopandas
import pandas
import datetime

import util

if __name__ == '__main__':
    # 4.15 - 5.17 疫情
    covid_df = pandas.read_csv('covid_with_gps.csv', engine='python', skip_blank_lines=True)
    site_df = pandas.read_csv('F:\myStuff\数据\仓_gps_营业部_polygon_\上海营业站位置信息with合并围栏.csv', engine='python',
                              skip_blank_lines=True)
    site_df['fence'] = geopandas.GeoSeries.from_wkt(site_df['fence'])
    site_df = geopandas.GeoDataFrame(site_df, geometry='fence')
    site_df.sort_values(ascending=True, inplace=True, by=['county_name'])
    site_df.index = site_df['site_code']
    districts = list(site_df['county_name'].unique())

    covid_df['dt'] = pandas.to_datetime(covid_df['dt'], format='%Y/%m/%d')
    covid_df = covid_df[['id', 'city', 'control_type', 'county', 'town', 'subdivision', 'dt', 'lng', 'lat']]
    covid_df.sort_values(ascending=True, inplace=True, by=['dt'])

    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date
    while cur_date <= end_date:
        # 获得疫情数据
        tomorrow = (cur_date + datetime.timedelta(days=1))
        covid_df_i = covid_df[(covid_df['dt'] >= cur_date) & (covid_df['dt'] < tomorrow)]
        covid_df_i.sort_values(ascending=True, inplace=True, by=['county'])
        for county in districts:
            covid_df_i_county = covid_df_i[covid_df_i['county'] == county]
            print(cur_date, ' ', county, '有', covid_df_i_county.shape[0], '条疫情数据\n')
            site_df_county = site_df[site_df['county_name'] == county]
            site_df_county.index = site_df_county['site_code']
            print(county, '有', site_df_county.shape[0], '个营业部\n\n')
            for index, row in site_df_county.iterrows():
                polygon = row['fence']
                isEmpty = True
                for i, r in covid_df_i_county.iterrows():
                    testx = r['lng']
                    testy = r['lat']
                    if util.pnpoly(testx, testy, polygon):
                        # 点在多边形内
                        if isEmpty:
                            site_df.at[index, cur_date.strftime("%m-%d")] = str(r['id']) + '-' + r['control_type'] + ";"
                            isEmpty = False
                        else:
                            site_df.at[index, cur_date.strftime("%m-%d")] += str(r['id']) + '-' + r[
                                'control_type'] + ";"
                        # break
        cur_date += datetime.timedelta(days=1)
    site_df.to_csv('site_df_with_covid_info.csv', index=False)
