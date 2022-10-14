import pandas
from matplotlib import pyplot as plt
import seaborn as sns
from matplotlib.ticker import MultipleLocator


def formatDate(df):
    df.sort_values(by='create_time', inplace=True)
    df['create_time'] = df['create_time'].dt.strftime('%m-%d')
    return df


def analyse():
    df1 = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓/仓调配_20221012205053.csv', encoding='gbk',
        parse_dates=['op_date', 'create_time'],
        engine='python', skip_blank_lines=True)
    df2 = pandas.read_csv(
        '/Users/lyam/同步空间/数据/仓/调拨出库_20221012232432.csv', encoding='gbk',
        parse_dates=['op_date', 'create_time'],
        engine='python', skip_blank_lines=True)
    df1.dropna(subset=['status_map'], inplace=True)
    df1.drop_duplicates(inplace=True)

    # df1['outside_num_c'] = (
    #     df1['outside_num'].groupby(df1['inside_no']).transform('sum'))
    # df1['inside_num_c'] = (
    #     df1['inside_num'].groupby(df1['inside_no']).transform('sum'))
    # df_no1 = df1.drop_duplicates(subset=['inside_no'])
    # df_id1 = df1.drop_duplicates(subset=['outside_id'])
    # df_id1 = formatDate(df_id1)

    df2.dropna(subset=['status_map'], inplace=True)
    df2.drop_duplicates(inplace=True)

    df2['plan_num_c'] = (
        df2['plan_num'].groupby(df2['outside_no']).transform('sum'))
    df2['reality_num_c'] = (
        df2['reality_num'].groupby(df2['outside_no']).transform('sum'))

    print(len(df2['outside_no'].unique()))
    print(len(df2['outside_id'].unique()))
    df_no2 = df2.drop_duplicates(subset=['outside_no'])
    print(len(df_no2['outside_id'].unique()))
    df_id2 = df2.drop_duplicates(subset=['outside_id'])
    print(len(df_id2['outside_id'].unique()))
    df_id2 = formatDate(df_id2)

    df_no2_res = df_no2.groupby(['create_time', 'outside_no'])['reality_num_c'].sum().unstack(fill_value=0)
    df_no2_res["mean"] = df_no2_res.apply(lambda x: x.mean(), axis=1)
    # 1. 验证仓和仓之间的互动在疫情期间增加，也就是调拨的次数增加/调拨的货物数量增加
    # 一个outside_id 代表一次出入库，对应多个inside_no货物箱, 每个inside_no 对应一个status
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # 比较疫情和常规下，调拨次数分析
    # df1_freq = df_id1.groupby('create_time').size().reset_index(name='distribute_qty')
    # ax = sns.lineplot(data=df1_freq, y='distribute_qty', x='create_time')

    df2_freq = df_id2.groupby('create_time').size().reset_index(name='distribute_qty')
    ax = sns.lineplot(data=df2_freq, y='distribute_qty', x='create_time')
    ax.xaxis.set_major_locator(MultipleLocator(7))
    ax.grid(True)
    ax.set_xlabel('日期')
    ax.set_ylabel('调拨次数')
    ax.set_title('仓仓调拨次数分析')

    ax2 = ax.twinx()
    sns.barplot(data=df_no2_res, x='create_time', y='mean', ax=ax2)
    ax2.set_ylabel('调拨单量')

    s1 = 150 / plt.gcf().dpi * 10
    margin = 0.5 / plt.gcf().get_size_inches()[0]
    plt.gcf().subplots_adjust(left=margin, right=1. - margin)
    plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
    plt.savefig('pngs/调拨/仓仓调拨次数分析.png')
    plt.show()
    exit(0)
    df2_may_fail = df2[[df2['outside_status'] <= 40]]
    df2_success = df2

    # 先不考虑 失败的
    # 有问题的 需要去merge df1
    df2_fail = df2[df2['outside_status'] <= 40][['outside_id']].drop_duplicates()
    df1_fail_info = df1[df1['outside_id'].isin(list(df2_fail['outside_id']))]
    # 在2fail的在1有记录
    df_fail = pandas.read_csv(
        'id_not_in.csv',
        engine='python', skip_blank_lines=True)
    # df1.drop_duplicates(inplace=True)
    df2.drop_duplicates(inplace=True)

    # 计划出库和实际出库差值
    df2.drop(['line_num', 'outside_type', 'create_user', 'goods_name', 'seller_name', 'dept_name', 'op_date'], axis=1,
             inplace=True)
    df2.dropna(subset=['status_map'], inplace=True)
    df2 = df2.rename(columns={'outside_no': '出A库单号', 'plan_num': '计划出A库数量', 'reality_num': '实际出A库数量',
                              'outside_status': '出A库状态', 'status_map': '出B库map', 'status_key': '出B库状态码'})
    df2.drop_duplicates(inplace=True)
    df = pandas.merge(df1, df2, on='outside_id', how='outer')

    df.sort_values(by='create_time', inplace=True)
    df['create_time'] = df['create_time'].dt.strftime('%m-%d')
    df.to_csv('merged_1_2.csv', index=False)
    exit(0)
    df_in = df[df['outside_status'] == 30]
    df_not_in = df[df['outside_status'] != 30]
    df1_not_in_id = df1_not_in[['outside_id']].drop_duplicates()
    df1_not_in_id.to_csv('id_not_in.csv', index=False)

    # 计划配送和实际配送分析
    df2['diff'] = df2['plan_num'] - df2['reality_num']
    df2['sum_diff'] = (df2['diff'].groupby(df2['create_time']).transform('mean'))
    df2_t = df2[['sum_diff', 'create_time']].drop_duplicates()

    ax = sns.lineplot(data=df2_t, y='sum_diff', x='create_time')
    ax.xaxis.set_major_locator(MultipleLocator(7))
    plt.show()

    exit(0)

    df1 = pandas.read_csv(
        'temp1.csv',
        parse_dates=['op_date', 'create_time'],
        engine='python', skip_blank_lines=True)
    df1.drop(['line_num', 'box_no', 'goods_name', 'seller_name', 'dept_name', 'op_date'], axis=1,
             inplace=True)
    df1.drop_duplicates(inplace=True)
    df1.sort_values(by='create_time', inplace=True)
    df1['create_time'] = df1['create_time'].dt.strftime('%m-%d')

    #
    exit(0)

    # l1 = len(df1['warehouse_name_out'].unique()) #413
    # l2 = len(df2['warehouse_name_out'].unique()) #422
    # l3 = len(df1['warehouse_no_out'].unique()) #389
    # l4 = len(df2['warehouse_no_out'].unique()) #398
    # status = (df2['outside_status'].unique()) # [82 20 81 80 90 10 30 65 50 40]
    pass


if __name__ == '__main__':
    analyse()
