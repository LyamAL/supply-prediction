import os
import re

import pandas as pd
import requests as requests
from matplotlib import pyplot as plt


def geocodeB(address):
    """
    @ address: 名称字符串
    @ 返回值：经度，纬度
    """
    base_url = "http://api.map.baidu.com/geocoder?address={address}&output=json&key=TaMeTaBAcffNbvUSxEeRarCSpuYgDwQ7".format(
        address=address)

    response = requests.get(base_url)
    try:
        answer = response.json()
        latitude = answer['result']['location']['lat']
        longitude = answer['result']['location']['lng']
    except Exception:
        re_express = re.compile('(\d+[弄]?.+$)')
        res = re_express.match(address)
        return 0, 0

    return longitude, latitude


def convert_street_to_gps():
    df = pd.read_csv('lockdown_03010820.csv', engine='python', skip_blank_lines=True)
    df['addr'] = df.apply(lambda x: '上海市' + x['area'] + x['road'], axis=1)
    df[['lng', 'lat']] = df.apply(lambda x: geocodeB(x['addr']), axis=1, result_type='expand')
    df.to_csv('lockdown_03010820_gps.csv')


def locate():
    # df = pd.read_csv('lockdown_03010820.csv', engine='python', skip_blank_lines=True)
    # df.at[13, 'road'] = '大场镇乾溪一村小区'
    # df['road'] = df['road'].str.replace('\n', ' ', regex=True)

    df_tuotou = pd.read_csv('F:\myStuff\供应预测\数据\妥投数据.csv', engine='python', skip_blank_lines=True)
    df_tuotou = df_tuotou[['node_code', 'node_name', 'lng', 'lat']]
    df_tuotou.drop_duplicates(subset=['node_name'], inplace=True)
    df_tuotou.to_csv('site_gps.csv')
    exit(0)
    df.drop('Unnamed: 0', inplace=True, axis=1)
    return df


# filePath = 'xx/xx/xx/' 路径下默认全都是'2022-xx-xx.csv'格式的csv文件
def repo_visual(filePath):
    lst = os.listdir(filePath)
    df_all = pd.DataFrame()
    for i in lst:
        df = pd.read_csv(filePath + i, engine='python', skip_blank_lines=True, parse_dates=['dt'])
        df = df.dropna(subset=['warehouse_no'])
        df = df.dropna(subset=['distribute_no'])

        df['out_ord_flag'] = df['out_ord_flag'].astype(str)
        df['distribute_no'] = df['distribute_no'].astype(int)
        df['warehouse_no'] = df['warehouse_no'].astype(int)

        df = df[df['out_ord_flag'] == '自营']  # 选自营的
        df = df[df['dim_delv_center_name'].str.contains('上海')]  # 选上海的

        df['md'] = df['dt'].apply(lambda x: x.strftime('%m-%d'))  # 获得04-26
        df = df[['md', 'package_qty', 'rec_qty', 'unfin_qty', 'order_qty', 'valid_order_qty', 'warehouse_no']]

        df_all = pd.concat([df_all, df], ignore_index=True)  # 每个csv都concat起来

    df_all.to_csv('sh_repo_all.csv')  # 备份

    df_all['package_qty'] = df_all['package_qty'].astype(int)
    df_all['rec_qty'] = df_all['rec_qty'].astype(int)
    df_all['unfin_qty'] = df_all['unfin_qty'].astype(int)
    df_all['order_qty'] = df_all['order_qty'].astype(int)
    df_all['valid_order_qty'] = df_all['valid_order_qty'].astype(int)

    df_t1 = df_attributed(df_all, 'package_qty')
    df_t2 = df_attributed(df_all, 'rec_qty')
    df_t3 = df_attributed(df_all, 'unfin_qty')
    df_t4 = df_attributed(df_all, 'order_qty')
    df_t5 = df_attributed(df_all, 'valid_order_qty')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    plt.figure(figsize=(12, 10))

    # 横轴刻度 指定步长显示
    # fig, ax = plt.subplots()
    # ax.xaxis.set_major_locator(MultipleLocator(2)) #每隔两个显示

    df_t1['res'].plot(kind='line', legend=True, label='总单量')
    df_t2['res'].plot(kind='line', legend=True, label='接收单量')
    df_t3['res'].plot(kind='line', legend=True, label='未生产单量')
    df_t4['res'].plot(kind='line', legend=True, label='当日总下单量')
    df_t5['res'].plot(kind='line', legend=True, label='有效单量')

    plt.ylabel('数量')
    plt.xlabel('日期')
    plt.title('上海仓库每日平均单量分析')
    # plt.title('上海仓库每日总单量分析')
    plt.savefig('./上海仓库每日平均单量分析')
    # plt.savefig('./上海仓库每日总单量分析')
    plt.show()
    exit(0)


if __name__ == '__main__':
    locate()
    exit(0)
    # df1 = pd.read_csv('restraint_03010608.csv', engine='python', skip_blank_lines=True)
    # df2 = pd.read_csv('restraint_06090820.csv', engine='python', skip_blank_lines=True)
    # df1.drop('Unnamed: 0', inplace=True, axis=1)
    # df2.drop('Unnamed: 0', inplace=True, axis=1)
    # df2.drop('dt', inplace=True, axis=1)
    # df2.drop('is_cancel', inplace=True, axis=1)
    # df2['level'] = df2['level'].str.replace('风险区', '风险地区', regex=True)
    # # df1['road'] = df1['road'].apply(lambda x: 0 if x[0].isdigit() else x)
    # # df1 = df1[df1['road'] != 0]
    # # df1.loc[65, 'area'] = '闵行区'
    # # df1.loc[54, 'area'] = '浦东新区'
    # # df1.loc[53, 'area'] = '浦东新区'
    # # df1.loc[52, 'area'] = '浦东新区'
    # # df1.loc[55, 'area'] = '浦东新区'
    #
    # df = pd.concat([df1, df2])
    # df.to_csv('lockdown_03010820.csv')
    # exit(0)

    # df = pd.read_csv('result.csv', engine='python', skip_blank_lines=True)
    # df.dropna(inplace=True, subset=['info'])
    # df = df[['publish_date', 'href', 'area', 'road', 'level', 'info']]
    # df['info'] = df['info'].str.replace('^.*经市新冠肺炎疫情防控工作领导小组办公室研究决定，', '', regex=True)
    # df['info'] = df['info'].str.replace('^.*经市新冠肺炎疫情防控工作领导小组办公室研究，', '', regex=True)
    # df['info'] = df['info'].str.replace('^.*经市防控办研究决定，', '', regex=True)
    # df['info'] = df['info'].str.replace('^.*经市防控办研究，', '', regex=True)
    # df['info'] = df['info'].str.replace('，上海市其他区域风险等级不变。', '', regex=True)
    #
    # # replace 正则
    # re_express = re.compile('将(.+)由?.*[列调整]为(.{4}区)')
    # df[['road', 'level']] = df['info'].str.extract(re_express, expand=False)
    #
    # df['road'] = df['road'].str.replace('由中.*$', '', regex=True)
    # df['road'] = df['road'].str.replace('由高.*$', '', regex=True)
    # df['road'] = df['road'].str.replace('由低.*$', '', regex=True)
    # df['road'] = df['road'].str.replace('^将', '', regex=True)
    # df['road'] = df['road'].str.replace('，', '', regex=True)
    # df['road'] = df['road'].str.replace('。', '', regex=True)
    # df_res = pd.DataFrame().reindex_like(df)
    # for index, row in df.iterrows():
    #     ls = row['road'].split('、')
    #     if len(ls) > 1:
    #         print(row['road'])
    #         for i in ls:
    #             data = {'publish_date': row['publish_date'], 'href': row['href'], 'road': i,
    #                     'level': row['level']}
    #             # df.at[index, 'road'] = 0
    #             df_res = df_res.append([data], ignore_index=True)
    #     else:
    #         data = {'publish_date': row['publish_date'], 'href': row['href'], 'road': row['road'],
    #                 'level': row['level']}
    #         df_res = df_res.append([data], ignore_index=True)
    #
    # df_res.dropna(inplace=True, subset=['road'])
    # df_res['road'] = df_res['road'].apply(lambda x: 0 if x[0].isdigit() else x)
    # df1 = df_res[df_res['road'] != 0]
    # df_res['area'] = df_res['road'].str.extract('(^.{2,3}区)', expand=False)
    # df_res['road'] = df_res['road'].str.replace('(^.{2,3}区)', '', regex=True)
    # df_res.loc[74, 'area'] = '闵行区'
    # df_res.loc[62, 'area'] = '浦东新区'
    # df_res.loc[60, 'area'] = '浦东新区'
    # df_res.loc[61, 'area'] = '浦东新区'
    # df_res.loc[63, 'area'] = '浦东新区'
    # df_res.drop('info', inplace=True, axis=1)
    # df_res.dropna(subset=['road'], inplace=True)
    # df_res.to_csv('restraint_03010608.csv')
    # # df.to_csv('restraint_03010608.csv')
    # print(df.shape[0])
    # exit(0)
