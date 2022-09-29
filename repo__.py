import os

import pandas as pd
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

        df = df[df['out_ord_flag'] != '自营']  # 选自营的
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
