import datetime

import pandas
import shapely.geometry

import util
from features_construction import toGeoFence

if __name__ == '__main__':
    # df1 = pandas.read_csv('F:\myStuff\数据\仓_gps_营业部_polygon_\上海营业站位置信息_20220904222813.csv', engine='python',
    #                       skip_blank_lines=True)
    # df2 = pandas.read_csv('sh_site_fence_1.csv', engine='python',
    #                         skip_blank_lines=True)
    # df1 = df1[['site_code', 'node_name', 'county_id', 'county_name', 'town_id', 'town_name', 'address', 'lng', 'lat']]
    # df = pandas.merge(df1, df2, on='site_code', how='right')
    # df.dropna(subset=['site_name'], inplace=True)
    # df.drop('city_name', inplace=True, axis=1)
    # df.drop('site_name', inplace=True, axis=1)
    # df.to_csv('上海营业站位置信息with合并围栏.csv', index=False)
    # exit(0)
    covid_df = pandas.read_csv('/Users/lyam/同步空间/数据/疫情数据/covid_with_jd_gps.csv', engine='python',
                               skip_blank_lines=True, encoding='utf-8',
                               parse_dates=['dt'])
    covid_df = covid_df[['id', 'control_type', 'county', 'town', 'subdivision', 'dt', 'lng', 'lat']]
    covid_df.sort_values(ascending=True, inplace=True, by=['dt'])
    # # 4.15 - 5.17 疫情和营业部/仓对上 point in polygon
    # covid_df.sort_values(by=['dt'], inplace=True)
    # covid_df = covid_df[['lat', 'lng', 'id']]
    # covid_raw = pandas.read_csv('F:\myStuff\数据\疫情数据\covid_with_gps.csv', engine='python', skip_blank_lines=True,
    #                            parse_dates=['dt'])
    # covid_raw = covid_raw[['id', 'city', 'control_type', 'county', 'town', 'subdivision', 'dt']]
    # covid_df = pandas.merge(covid_df, covid_raw, on='id', how='left')
    # covid_df.to_csv('F:\myStuff\数据\疫情数据\covid_with_jd_gps.csv', index=False)
    # exit(0)
    site_df = pandas.read_csv('/Users/lyam/同步空间/数据/营业站/site_revised_gps_v2.csv',
                              engine='python',
                              skip_blank_lines=True)
    site_df = toGeoFence(site_df, 'fence')
    site_df.sort_values(ascending=True, inplace=True, by=['county_name'])
    site_df.index = site_df['site_code']
    districts = list(site_df['county_name'].unique())
    # covid_df_valid = covid_df[covid_df['lat'] != 0.0]
    # covid_df_invalid = covid_df[covid_df['lat'] == 0.0]
    # print(covid_df_valid.shape[0] / covid_df.shape[0])

    # 解析gps
    # covid_df['subdivision'] = covid_df['subdivision'].str.replace('?', '', regex=False)
    # covid_df['subdivision'] = covid_df['subdivision'].str.replace('（', '(', regex=False)
    # covid_df['subdivision'] = covid_df['subdivision'].str.replace('）', ')', regex=False)
    # covid_df_invalid[['lng', 'lat']] = covid_df_invalid.apply(
    #     lambda x: util.geocodeB(x['city'] + x['county'] + x['town'] + x['subdivision'][5:9]), axis=1, result_type="expand")

    # 现将表构成list，然后在作为concat的输入
    # frames = [covid_df_valid, covid_df_invalid]
    #
    # covid_df_all = pandas.concat(frames)
    # covid_df_all.to_csv('covid_with_gps.csv', index=False)
    # exit(0)

    # 营业部的polygon

    start_date = datetime.datetime(2022, 4, 15, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 5, 17, hour=23, minute=0, second=0)
    cur_date = start_date
    while cur_date <= end_date:
        tomorrow = (cur_date + datetime.timedelta(days=1))
        covid_df_i = covid_df[(covid_df['dt'] >= cur_date) & (covid_df['dt'] < tomorrow)]
        covid_df_i.sort_values(ascending=True, inplace=True, by=['county'])
        for county in districts:
            covid_df_i_county = covid_df_i[covid_df_i['county'] == county]
            print(cur_date, ' ', county, '有', covid_df_i_county.shape[0], '条疫情数据')
            site_df_county = site_df[site_df['county_name'] == county]
            site_df_county.index = site_df_county['site_code']
            print(county, '有', site_df_county.shape[0], '个营业部')
            for index, row in site_df_county.iterrows():
                isEmpty = True
                for i, r in covid_df_i_county.iterrows():
                    if util.pnpolyShaple(row['fence'], shapely.geometry.Point(r['lng'], r['lat'])):
                        if isEmpty:
                            site_df.at[index, cur_date.strftime("%m-%d")] = str(r['id']) + '-' + r['control_type'] + ";"
                            isEmpty = False
                        else:
                            site_df.at[index, cur_date.strftime("%m-%d")] += str(r['id']) + '-' + r[
                                'control_type'] + ";"
                        # break
        cur_date += datetime.timedelta(days=1)
    site_df.to_csv('/Users/lyam/同步空间/数据/疫情场景数据/site_with_covid_info_v3.csv', index=False)

