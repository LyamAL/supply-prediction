from pyecharts.globals import GeoType
from pyecharts import options
import webbrowser
import pandas
from pyecharts.charts import BMap, Geo
from pyecharts.commons.utils import JsCode

from matplotlib import pyplot as plt
if __name__ == '__main__':
    df = pandas.read_csv('F:\myStuff\数据\\20220926_new\上海_1_8月_仓_出站量_20220926175203.csv', engine='python', skip_blank_lines=True
                         , parse_dates=['real_delv_tm_c'])
    df.dropna(subset=['sale_ord_count'], inplace=True)
    df.dropna(subset=['real_delv_tm_c'], inplace=True)
    df['md'] = df['real_delv_tm_c'].apply(lambda x: x.strftime('%m-%d'))
    df_t = df.groupby(['site_id_c', 'md'])['sale_ord_count'].sum().unstack()
    df_t = df_t.fillna(0)
    df_t["res"] = df_t.apply(lambda x: x.mean(), axis=1)
    plt.figure(figsize=(10, 8))
    df_t['res'].plot(legend=True, label='营业部当日妥投均量')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    df_repo = pandas.read_csv('F:/myStuff/供应预测/数据/常规数据/常规出仓.csv', engine='python', skip_blank_lines=True
                              , parse_dates=['start_opt_day'])

    # df_repo.dropna(subset=['countwaybill'], inplace=True)
    # df_repo.dropna(subset=['dt'], inplace=True)
    df_repo['md'] = df_repo['start_opt_day'].apply(lambda x: x.strftime('%m-%d'))
    df_t = df_repo.groupby(['md', 'end_node_id'])['waybill_count'].sum().unstack()
    df_t = df_t.fillna(0)
    df_t["res"] = df_t.apply(lambda x: x.mean(), axis=1)
    df_t['res'].plot(legend=True, label='仓库当日处理量')

    plt.ylabel('日均量')
    plt.xlabel('日期')
    plt.title('2021站点日妥投总量和仓处理量(0308-0731)')
    plt.savefig('./2021站点日妥投总量和仓处理量(0308-0731)')
    plt.show()
    exit(0)

    # g = Geo()
    # g.add_schema(maptype="上海")
    #
    # data_pair = list()
    # mean_cwb = df['countwaybill'].mean()
    # mx = (df['countwaybill'].max())
    # mn = (df['countwaybill'].min())
    #
    # for index, row in df.iterrows():
    #     cwb = row['countwaybill']
    #     if abs(cwb) > mean_cwb:
    #         # df.at[index, 2] = cwb
    #         g.add_coordinate(row['node_name'], row['lng'], row['lat'])
    #         data = (row['node_name'], cwb)
    #         data_pair.append(data)
    #
    # # data_pair = [(row['0_y'], row[2]) for index, row in df.iterrows()]
    # # 画图
    # g.add('', data_pair, type_=GeoType.EFFECT_SCATTER, symbol_size=2, label_opts=options.LabelOpts(is_show=True))
    # g.set_series_opts(label_opts=options.LabelOpts(is_show=False, formatter=JsCode(
    #     """function(params) {
    #     if ('value' in params.data) {
    #         return params.data.value[2];
    #     }
    # }"""
    # )))
    #
    # g.set_global_opts(title_opts=options.TitleOpts(title="上海市0308-0731营业部妥投量"),
    #                   legend_opts=options.LegendOpts(is_show=False),
    #                   visualmap_opts=options.VisualMapOpts(
    #                       max_=mx, min_=mn, is_piecewise=True
    #                   ))
    #
    # # 保存结果到 html
    # result = g.render('site_tuotou_0318_0731.html')
    # webbrowser.open_new_tab(result)
