import pandas
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

from warehouse_type_addr import drawByCities


def draw():
    df_res1 = pandas.read_csv(
        '../temp_1_2_7_8_sale_city.csv',
        engine='python',
        skip_blank_lines=True)
    df_res2 = pandas.read_csv(
        '../temp_3_6_sale_city.csv',
        engine='python',
        skip_blank_lines=True)
    df_res3 = pandas.read_csv(
        '../temp_7_8_sale_city.csv',
        engine='python',
        skip_blank_lines=True)
    df_res2['city'] = df_res2['city'].str.replace('市', '', regex=False)
    df_res1['city'] = df_res1['city'].str.replace('市', '', regex=False)
    df_res3['city'] = df_res3['city'].str.replace('市', '', regex=False)

    # drawAll(df_res1, '1_2月')
    # drawAll(df_res2, '3_6月')
    # drawAll(df_res3, '7_8月')

    drawByCities(df_res1, '1_2_7_8月')
    # drawByCities(df_res2, '3_6月')
    # drawByCities(df_res3, '7_8月')


if __name__ == '__main__':
    # draw()
    stats_df = pandas.read_csv(
        'temp_1116_routes_freq.csv',
        engine='python',
        skip_blank_lines=True)
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    ax = stats_df.plot.bar(x='value', y='cdf')

    s1 = 50 / plt.gcf().dpi * 10
    margin = 0.5 / plt.gcf().get_size_inches()[0]
    plt.gcf().subplots_adjust(left=margin, right=1. - margin)
    plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
    ax.xaxis.set_major_locator(MultipleLocator(20))
    plt.show()
