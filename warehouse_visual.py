from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt


def vvvvvisual(firepath):
    df = pd.read_csv(firepath, engine='python', skip_blank_lines=True, parse_dates=['sale_ord_dt'])
    df = df[df['first_cate_name'] == '自营']  # 选自营的
    df = df[df['store_name'].str.contains('上海')]  # 选上海的仓库
    df['package_qtty'] = df['package_qtty'].astype(int)
    df['out_wh_tm'] = pd.to_datetime(df['out_wh_tm'], format='%Y-%m-%d')
    df['succ_delv_tm'] = pd.to_datetime(df['succ_delv_tm'], format='%Y-%m-%d')
    df.dropna(subset=['succ_delv_tm'], inplace=True)
    df.dropna(subset=['out_wh_tm'], inplace=True)
    df.dropna(subset=['sale_ord_dt'], inplace=True)

    df['sale_ord_dt'] = df['sale_ord_dt'].apply(
        lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))
    df['out_wh_tm'] = df['out_wh_tm'].apply(
        lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))
    df['succ_delv_tm'] = df['succ_delv_tm'].apply(
        lambda x: int(x.replace(hour=0, minute=0, second=0).timestamp()))

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(12, 10))

    my_x_ticks = list(df['succ_delv_tm'].unique())
    my_x_ticks.sort()
    my_x_ticks = my_x_ticks[::2]
    ax_xlabels = [((datetime.fromtimestamp(i)).strftime("%m-%d")) for i in my_x_ticks]
    plt.xticks(ticks=my_x_ticks, labels=ax_xlabels, rotation=30)

    df_temp = df.groupby(['sale_ord_dt', 'store_id'])['package_qtty'].sum().unstack()
    df_temp.fillna(0, inplace=True)
    df_temp["sum"] = df_temp.apply(lambda x: x.sum(), axis=1)
    df_temp['sum'].plot(marker='*', ms=10, legend=True, label='下单量')

    # 出仓量 = out_wh_tm
    df_temp = df.groupby(['out_wh_tm', 'store_id'])['package_qtty'].sum().unstack()
    df_temp.fillna(0, inplace=True)
    df_temp["sum"] = df_temp.apply(lambda x: x.sum(), axis=1)
    df_temp['sum'].plot(marker='o', ms=8, legend=True, label='出仓量')

    # 妥投量 = succ_delv_tm
    df_temp = df.groupby(['succ_delv_tm', 'store_id'])['package_qtty'].sum().unstack()
    df_temp.fillna(0, inplace=True)
    df_temp["sum"] = df_temp.apply(lambda x: x.sum(), axis=1)
    df_temp['sum'].plot(marker='v', ms=8, legend=True, label='妥投量')

    plt.ylabel('单量')
    plt.xlabel('日期')
    plt.title('仓库下单量/出库量/妥投量')
    plt.savefig('./仓库单量分析')
    plt.show()
    exit(0)


if __name__ == '__main__':
    firepath = 'F:\myStuff\数据\仓_gps_营业部_polygon_/test_20220905104052.csv'
    vvvvvisual(firepath)
