import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

if __name__ == '__main__':

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # df = df[['stat_date', 'site_code', 'max_succ_delv_tm', 'deliver_num', 'site_name', 'site_province_name',
    #          'site_city_name', 'site_area_name']]
    # df['md'] = df['stat_date'].apply(lambda x: x.strftime('%m-%d'))
    # df['max_succ_delv_tm'] = pd.to_datetime(df['max_succ_delv_tm'], format='%Y-%m-%d %H:%M:%S')
    # df.to_csv('df_daily_info_site.csv')
    # exit(0)
    # df1 = pd.pivot_table(df, index=[u'site_code', u'md'], values=[u'deliver_num'], aggfunc=[np.sum])
    # df1 = pd.read_csv('df_pivot_table.csv', engine='python', skip_blank_lines=True)

    # df = pd.read_csv('df_daily_info_site.csv', engine='python', skip_blank_lines=True, parse_dates=['stat_date'])
    # df.drop('Unnamed: 0', axis=1, inplace=True)
    # df1 = pd.merge(df, df2, on='site_code', how='right')
    # df = df1[['site_code', 'deliver_num', 'md']]
    # df.dropna(axis=0, how='any')  # drop all rows that have any NaN values
    #
    # res1 = df.groupby(df['site_code'])['md'].value_counts().unstack(fill_value=0)
    # res2 = df.groupby(df['md'])['site_code'].value_counts().unstack(fill_value=0)
    #
    # res1["sum"] = res1.apply(lambda x: sum(x), axis=1)
    # res2["sum"] = res2.apply(lambda x: sum(x), axis=1)
    # res1.to_csv('df_site_date_sh.csv')
    # res2.to_csv('df_date_site_sh.csv')
    # df1 = pd.pivot_table(df, index=[u'site_code'], values=[u'deliver_num'], aggfunc=[np.sum])
    # df2 = pd.pivot_table(df, index=[u'md'], values=[u'deliver_num'], aggfunc=[np.sum])
    # exit(0)

    # plt.figure(figsize=(12, 10))
    # df = pd.read_csv('df_date_site_sh.csv', engine='python', skip_blank_lines=True)
    # df.set_index(["md"], inplace=True)
    #
    # df['sum'].plot(figsize=(8, 6))
    # plt.ylabel('当日妥投量')
    # plt.xlabel('日期')
    # plt.title('上海站点的每日妥投总量(3.15-7.20)')
    # plt.savefig('./上海站点的每日妥投总量(3_15-7_20)')
    # plt.show()


    fig, ax = plt.subplots()

    df = pd.read_csv('df_daily_info.csv', engine='python', skip_blank_lines=True,parse_dates=['stat_date'])
    df.sort_values("md", inplace=True, ascending=True)
    plt.ylabel('妥投量')
    plt.xlabel('日期')
    plt.title('疫情期间上海各站点的妥投量分布(0426-0531)')
    ax.xaxis.set_major_locator(MultipleLocator(8))
    sns.lineplot(x="md", y="deliver_num", markers="o", data=df)
    plt.legend(labels=['上海各站点'], loc='upper right')
    plt.savefig('./上海各站点的妥投量分布(0426-0531)')
    plt.show()
