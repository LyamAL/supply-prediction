import os

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


def df_attributed(df, col):
    df_t = df.groupby(['md', 'warehouse_no'])[col].sum().unstack()  # 收集每天每个站点产生的对应单量
    df_t = df_t.fillna(0)
    df_t["res"] = df_t.apply(lambda x: x.mean(), axis=1)  # 求每个站点的均值
    # df_t["res"] = df_t.apply(lambda x: x.sum(), axis=1)  # 求所有站点总和
    return df_t


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
    filePath = 'F:/myStuff/供应预测/4-26-5-12/'
    repo_visual(filePath)
    lst = os.listdir(filePath)
    df_o = pd.DataFrame()
    for i in lst:
        nm = 'sh_repo_' + i[5:-4] + '_all_.csv'
        df = pd.read_csv(filePath + i, engine='python', skip_blank_lines=True)
        df = df.dropna(subset=['warehouse_no'])
        df = df.dropna(subset=['distribute_no'])

        df['out_ord_flag'] = df['out_ord_flag'].astype(str)
        df['distribute_no'] = df['distribute_no'].astype(int)
        df['warehouse_no'] = df['warehouse_no'].astype(int)

        # df = df[df['out_ord_flag'] == '自营']
        df = df[df['dim_delv_center_name'].str.contains('上海')]
        code_lst = df['distribute_no'].unique()
        # df = df[df['distribute_no'].isin(code_lst)]
        df.drop('Unnamed: 0', axis=1, inplace=True)
        df.drop('out_ord_flag', axis=1, inplace=True)
        df.drop('distribute_no', axis=1, inplace=True)
        df.drop('dim_delv_center_name', axis=1, inplace=True)
        df.drop('garden_name', axis=1, inplace=True)
        df.drop('loc_region', axis=1, inplace=True)
        df.drop('recv_province', axis=1, inplace=True)
        df.drop('recv_region', axis=1, inplace=True)
        df.drop('province', axis=1, inplace=True)
        df.drop('city', axis=1, inplace=True)
        df['package_qty'] = df['package_qty'].astype(int)
        df['rec_qty'] = df['rec_qty'].astype(int)
        df['unfin_qty'] = df['unfin_qty'].astype(int)
        df['order_qty'] = df['order_qty'].astype(int)
        df['valid_order_qty'] = df['valid_order_qty'].astype(int)
        df.to_csv(nm)
        df_o = pd.concat([df_o, df], ignore_index=True)
    df_o.to_csv('sh_repo_0426_0512_all.csv')
    # exit(0)
    # repo_visual('F:/myStuff/供应预测/4-26-5-12/2022-04-26.csv')
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    # plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # fig, ax = plt.subplots()
    # ax.xaxis.set_major_locator(MultipleLocator(2))

df = pd.read_csv('sh_repo_0426_0512_ziying.csv', engine='python', skip_blank_lines=True, parse_dates=['dt'])
df['md'] = df['dt'].apply(lambda x: x.strftime('%m-%d'))
# df.set_index(["md"], inplace=True)
df = df[['package_qty', 'rec_qty', 'unfin_qty', 'order_qty', 'valid_order_qty', 'warehouse_no', 'md']]

df_t1 = df.groupby(['md', 'warehouse_no'])['package_qty'].sum().unstack()
df_t1 = df_t1.fillna(0)
df_t1["mean"] = df_t1.apply(lambda x: x.mean(), axis=1)

df_t2 = df.groupby(['md', 'warehouse_no'])['rec_qty'].sum().unstack()
df_t2 = df_t2.fillna(0)
df_t2["mean"] = df_t2.apply(lambda x: x.mean(), axis=1)

df_t3 = df.groupby(['md', 'warehouse_no'])['unfin_qty'].sum().unstack()
df_t3 = df_t3.fillna(0)
df_t3["mean"] = df_t3.apply(lambda x: x.mean(), axis=1)

df_t4 = df.groupby(['md', 'warehouse_no'])['order_qty'].sum().unstack()
df_t4 = df_t4.fillna(0)
df_t4["mean"] = df_t4.apply(lambda x: x.mean(), axis=1)

df_t5 = df.groupby(['md', 'warehouse_no'])['valid_order_qty'].sum().unstack()
df_t5 = df_t5.fillna(0)
df_t5["mean"] = df_t5.apply(lambda x: x.mean(), axis=1)

plt.figure(figsize=(12, 10))
df_t1['mean'].plot(kind='line', legend=True, label='总单量')
df_t2['mean'].plot(kind='line', legend=True, label='接收单量')
df_t3['mean'].plot(kind='line', legend=True, label='未生产单量')
df_t4['mean'].plot(kind='line', legend=True, label='当日总下单量')
df_t5['mean'].plot(kind='line', legend=True, label='有效单量')

# df.groupby('md')['package_qty'].sum().plot(kind='line', legend=True, figsize=(12, 10), label='总单量')
# df.groupby('md')['rec_qty'].sum().plot(kind='line', legend=True, figsize=(12, 10), label='接收单量')
# df.groupby('md')['unfin_qty'].sum().plot(kind='line', legend=True, figsize=(12, 10), label='未生产单量')
# df.groupby('md')['order_qty'].sum().plot(kind='line', legend=True, figsize=(12, 10), label='当日总下单量')
# df.groupby('md')['valid_order_qty'].sum().plot(kind='line', legend=True, figsize=(12, 10), label='有效单量')

plt.ylabel('数量')
plt.xlabel('日期')
plt.title('上海仓库每日平均单量分析(0426-0512)')
plt.savefig('./上海仓库每日平均单量分析2(0426-0512)')
plt.show()
exit(0)

# sns.lineplot(x="md", y="package_qty", markers="o", data=df, estimator=np.median)
# sns.lineplot(x="md", y="rec_qty", markers="o", data=df, estimator=np.median)
# sns.lineplot(x="md", y="unfin_qty", markers="o", data=df, estimator=np.median)
# sns.lineplot(x="md", y="order_qty", markers="o", data=df, estimator=np.median)
# sns.lineplot(x="md", y="valid_order_qty", markers="o", data=df, estimator=np.median)
plt.legend(labels=['总单量', '接收单量', '未生产单量', '当日总下单量', '有效单量'], loc='upper right')
plt.savefig('./上海仓库每日总单量分析2(0426-0512)')
plt.show()
exit(0)
