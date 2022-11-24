from datetime import timedelta

import numpy as np
import pandas
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


def fillna(df):
    ls = to_Date()
    df_all = pandas.DataFrame({'dt': ls}, columns=['dt'])
    df = pandas.merge(df, df_all, on=['dt'], how='right').fillna(0)
    df = df[['dt', 'res']]
    return df


def to_Date():
    low = datetime(2022, 1, 1)
    high = datetime(2022, 8, 15)
    cur = low
    lst = list()
    while cur <= high:
        lst.append(cur.strftime("%m-%d"))
        cur += timedelta(days=1)
    return lst


def draw(df, col1, col2):
    # 所有三方配送下 每天营业部能收到多少单 / 所有三方的仓库 每个营业站每天能收到多少单
    df_t = df.groupby(['dt', col1])[col2].sum().unstack()
    df_t = df_t.fillna(0)
    df_t["res"] = df_t.apply(lambda x: x.sum(), axis=1)
    df_t.reset_index(inplace=True)
    df_t = df_t[['dt', 'res']]
    return df_t


def filter_shanghai(df):
    cities = ['河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北',
              '湖南', '广东', '海南', '四川',
              '贵州', '云南', '陕西', '甘肃', '青海', '台湾', '北京', '天津', '重庆', '广东']
    for i in cities:
        df = df.drop(df[df['signed_sitename'].str.contains(i)].index)
        print(df.shape[0])

    print('----------------------')


def formatAxes(ax, title):
    ax.ticklabel_format(axis='y', style='sci', scilimits=[-5, 5])
    ax.xaxis.set_major_locator(MultipleLocator(12))
    ax.legend_.set_title(None)
    ax.grid(True)  # 显示网格
    ax.set_title(title, fontsize=15)
    ax.set_ylabel('日总量', fontsize=15)  # 设置子图的小标题
    ax.set_xlabel('日期', fontsize=15)
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(12)


if __name__ == '__main__':
    df_zy = pandas.read_csv('csvs/入站量—出仓量-2022-1-8.csv', engine='python', skip_blank_lines=True)
    df_zy['dt'] = pandas.to_datetime(df_zy['dt'], format='%m-%d')
    df_zy['dt'] = df_zy['dt'].apply(lambda x: (x.replace(year=2022)))

    df_repo = pandas.read_csv('/Users/lyam/同步空间/数据/三方数据/上海202203_202207三方配订单数据_20220819231133.csv',
                              engine='python',
                              skip_blank_lines=True, parse_dates=['start_opt_day'])
    df_send = pandas.read_csv('/Users/lyam/同步空间/数据/三方数据/上海202203_202207三方配妥投数据_20220819231205.csv',
                              engine='python',
                              skip_blank_lines=True, parse_dates=['signed_time_day'])
    df_repo.dropna(subset=['signed_sitename'], inplace=True)
    df_send.dropna(subset=['signed_sitename'], inplace=True)
    df_send.dropna(subset=['signed_time_day'], inplace=True)

    df_repo['dt'] = pandas.to_datetime(df_repo['start_opt_day'], format='%Y-%m-%d').dt.strftime('%m-%d')
    df_send['dt'] = pandas.to_datetime(df_send['signed_time_day'], format='%Y-%m-%d').dt.strftime('%m-%d')

    filter_shanghai(df_repo)
    filter_shanghai(df_send)

    from datetime import datetime

    df_repo_covid = df_repo[
        (df_repo['start_opt_day'] >= datetime(2022, 3, 1)) & (df_repo['start_opt_day'] < datetime(2022, 7, 1))]
    df_repo_normal = df_repo[
        (df_repo['start_opt_day'] >= datetime(2022, 7, 1)) | (df_repo['start_opt_day'] < datetime(2022, 3, 1))]
    df_send_covid = df_send[
        (df_send['signed_time_day'] >= datetime(2022, 3, 1)) & (df_send['signed_time_day'] < datetime(2022, 7, 1))]
    df_send_normal = df_send[
        (df_send['signed_time_day'] >= datetime(2022, 7, 1)) | (df_send['signed_time_day'] < datetime(2022, 3, 1))]
    df_zy_covid = df_zy[
        (df_zy['dt'] >= datetime(2022, 3, 1)) & (df_zy['dt'] < datetime(2022, 7, 1))]
    df_zy_normal = df_zy[
        (df_zy['dt'] >= datetime(2022, 7, 1)) | (df_zy['dt'] < datetime(2022, 3, 1))]
    df_zy_normal['dt'] = df_zy_normal['dt'].dt.strftime('%m-%d')
    df_zy_covid['dt'] = df_zy_covid['dt'].dt.strftime('%m-%d')

    df_send_covid_res = draw(df_send_covid, 'signed_sitecode', 'shipid_num')
    df_send_normal_res = draw(df_send_normal, 'signed_sitecode', 'shipid_num')
    df_repo_covid_res = draw(df_repo_covid, 'signed_sitecode', 'shipid_num')
    df_repo_normal_res = draw(df_repo_normal, 'signed_sitecode', 'shipid_num')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # fig, axes = plt.subplots(nrows=2, ncols=2, sharey=True, figsize=(20, 10))
    # fig.suptitle('自营和三方的出仓量和入站量对比', fontsize=20)
    # subplot1
    # axes1 = axes[0, 0]
    import seaborn as sns

    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    ax = sns.lineplot(x='dt', y='res', hue='type', data=df_zy_covid, palette=['#D98880', '#7DCEA0'])
    # sns.lineplot(x='dt', y='res', hue='type', data=df_zy_covid, palette=['#D98880', '#7DCEA0'], ax=axes1)
    formatAxes(ax, '疫情-自营订单-入站量-出仓量')
    plt.savefig('pngs/疫情-自营-入站量-出仓量.png')
    plt.show()

    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # axes2 = axes[0, 1]
    df_repo_covid_res['type'] = '三方-出仓量'
    df_send_covid_res['type'] = '三方-入站量'
    df_third_covid = pandas.concat([df_send_covid_res, df_repo_covid_res], axis=0)

    # axes2.plot(xaxis, df_t3['res'], color='#ff7f0e', ls='--', label='三方-营业部当日妥投总量')
    # axes2.plot(xaxis, df_t4['res'], color='#007f0e', ls='--', label='三方-仓库当日处理量')
    ax = sns.lineplot(x='dt', y='res', hue='type', data=df_third_covid, palette=['#D98880', '#7DCEA0'])
    # sns.lineplot(x='dt', y='res', hue='type', data=df_third_covid, palette=['#D98880', '#7DCEA0'], ax=axes2)
    formatAxes(ax, '疫情-三方-入站量-出仓量')
    plt.savefig('pngs/疫情-三方-入站量-出仓量.png')
    plt.show()

    # axes3 = axes[1, 0]
    # axes3.plot(xaxis, df_t5['res'], color='#ff7f0e', ls='--', label='自营-营业部当日妥投总量')
    # axes3.plot(xaxis, df_t6['res'], color='#007f0e', ls='--', label='自营-仓库当日处理量')
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    ax = sns.lineplot(x='dt', y='res', hue='type', data=df_zy_normal, palette=['#D98880', '#7DCEA0'])
    # sns.lineplot(x='dt', y='res', hue='type', data=df_zy_normal, palette=['#D98880', '#7DCEA0'], ax=axes3)
    formatAxes(ax, '常规-自营-入站量-出仓量(1/2/7/8月)')
    plt.savefig('pngs/常规-自营-入站量-出仓量.png')
    plt.show()

    df_repo_normal_res['type'] = '三方-出仓量'
    df_send_normal_res['type'] = '三方-入站量'
    df_third_normal = pandas.concat([df_repo_normal_res, df_send_normal_res], axis=0)
    # axes4 = axes[1, 1]
    # sns.lineplot(x='dt', y='res', hue='type', data=df_third_normal, palette=['#D98880', '#7DCEA0'], ax=axes4)
    ax = sns.lineplot(x='dt', y='res', hue='type', data=df_third_normal, palette=['#D98880', '#7DCEA0'])
    ax.ticklabel_format(axis='y', style='sci')
    ax.xaxis.set_major_locator(MultipleLocator(30))
    ax.legend_.set_title(None)
    ax.grid(True)  # 显示网格
    ax.set_title('常规-三方-入站量-出仓量(1/2/7/8月)', fontsize=15)
    ax.set_ylabel('日总量', fontsize=15)  # 设置子图的小标题
    ax.set_xlabel('日期', fontsize=15)
    plt.savefig('pngs/常规-三方-入站量-出仓量.png')
    plt.show()
