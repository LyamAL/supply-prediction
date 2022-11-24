from matplotlib import pyplot as plt
import pandas
from matplotlib.ticker import MultipleLocator


def series_cdf(s, attr, title):
    df = pandas.DataFrame(s).rename(columns={attr: 'value'})
    # Frequency
    stats_df = df.groupby('value') \
        ['value'] \
        .agg('count') \
        .pipe(pandas.DataFrame) \
        .rename(columns={'value': 'frequency'})
    # PDF
    stats_df['pdf'] = stats_df['frequency'] / sum(stats_df['frequency'])
    # CDF
    stats_df['cdf'] = stats_df['pdf'].cumsum()
    stats_df = stats_df.reset_index()

    # stats_df.to_csv('temp_1116_routes_freq.csv', index=False)
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    ax = stats_df.plot.bar(x='value', y='cdf')

    s1 = 50 / plt.gcf().dpi * 10
    margin = 0.5 / plt.gcf().get_size_inches()[0]
    plt.gcf().subplots_adjust(left=margin, right=1. - margin)
    plt.gcf().set_size_inches(s1, plt.gcf().get_size_inches()[1])
    # ax.xaxis.set_major_locator(MultipleLocator(15))
    plt.title(title)
    plt.savefig(f'pngs/cdfs/path_count/{title}.png')
    plt.show()
