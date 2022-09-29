from pyecharts.globals import GeoType
from pyecharts import options
import webbrowser
import pandas
from pyecharts.charts import BMap, Geo
from pyecharts.commons.utils import JsCode

from matplotlib import pyplot as plt


def res_df(df, col, str):
    df1 = df.groupby(['md', '委托书号'])[col].sum().unstack()
    df1 = df1.fillna(0)
    df1["res"] = df1.apply(lambda x: x.mean(), axis=1)
    df1['res'].plot(legend=True, label=str)


def md(df):
    df['md'] = df['委托书签收时间'].apply(lambda x: x.strftime('%m-%d'))
    df['实际在途时长'] = df['实际在途时长'].apply(lambda x: float(x[:-1]))


if __name__ == '__main__':
    # df = pandas.read_excel('F:/myStuff/供应预测/数据/抗役保供/上海目的地任务明细（3月27日～4月19日）.xlsx')
    # df = df[(df['始发市'] == '上海') & (df['目的市'] == '上海')]
    # df_ziying = df[df['承运商类型'] == '京东自营']
    # df_third = df[df['承运商类型'] == '三方']
    # df_ziying = df_ziying[['委托书号', '业务类型', '总单量', '提货网点类型', '卸货网点类型', '线路公里数', 'GPS行驶里程', '实际在途时长', '空车延误', '委托书创建时间','委托书应到时间','委托书签收时间']]
    # df_third = df_third[['委托书号', '业务类型', '总单量', '提货网点类型', '卸货网点类型', '线路公里数', 'GPS行驶里程', '实际在途时长', '空车延误', '委托书创建时间','委托书应到时间','委托书签收时间']]
    # df_third.to_csv('sh_third_car.csv')
    # df_ziying.to_csv('sh_ziying_car.csv')
    # exit(0)

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(10, 8))

    df_third = pandas.read_csv('sh_third_car.csv', engine='python', skip_blank_lines=True,
                               parse_dates=['委托书创建时间', '委托书应到时间', '委托书签收时间'])
    df_ziying = pandas.read_csv('sh_ziying_car.csv', engine='python', skip_blank_lines=True,
                                parse_dates=['委托书创建时间', '委托书应到时间', '委托书签收时间'])

    md(df_third)
    md(df_ziying)

    df_third_site = df_third[df_third['卸货网点类型'] == '站点']
    df_ziying_site = df_ziying[df_ziying['卸货网点类型'] == '站点']

    # res_df(df_third_site, '总单量', '疫情期间第三方货物运输的日均单量')
    # res_df(df_ziying_site, '总单量', '疫情期间自营货物运输的日均单量')

    res_df(df_third_site, '实际在途时长', '疫情期间第三方货物日均在途时长')
    res_df(df_ziying_site, '实际在途时长', '疫情期间自营货物日均在途时长')

    plt.ylabel('日均在途时长(小时)')
    plt.xlabel('日期')
    plt.title('疫情期间货物运输的日均在途时长对比分析(0327-0419)')
    plt.savefig('./疫情期间货物运输的日均在途时长对比分析(0327-0419)')

    plt.show()

