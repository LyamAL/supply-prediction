import datetime

import pandas
from folium import folium
from folium.plugins import HeatMap
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

from root_util import DISK_PATH_MACHINE


def warehouse_waybill_distribution():
    df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/20220926_new/上海_1_8月_仓_出仓量_20220926212042.csv', engine='python',
        parse_dates=['first_sorting_tm_c'],
        skip_blank_lines=True)
    addr_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
        skip_blank_lines=True)

    addr_df = addr_df[['store_id_c', 'delv_center_num_c', 'lat', 'lng', 'city']].drop_duplicates()
    df = df[['first_sorting_tm_c', 'store_id_c', 'delv_center_num_c', 'sale_ord_count']]

    df = pandas.merge(df, addr_df, on=['store_id_c', 'delv_center_num_c'], how='left').dropna(subset=['lat'])
    df = df[~df['city'].isin(['苏州市', '上海市'])]

    # df_covid = df[(df['first_sorting_tm_c'] < datetime.datetime(2022, 7, 1)) & (
    #         df['first_sorting_tm_c'] >= datetime.datetime(2022, 3, 1))]
    # df_normal = df[(df['first_sorting_tm_c'] < datetime.datetime(2022, 3, 1)) | (
    #         df['first_sorting_tm_c'] >= datetime.datetime(2022, 7, 1))]
    df_covid = df[(df['first_sorting_tm_c'] < datetime.datetime(2022, 5, 30)) & (
            df['first_sorting_tm_c'] >= datetime.datetime(2022, 3, 15))]
    df_covid = df_covid[['store_id_c', 'delv_center_num_c', 'lat', 'lng', 'sale_ord_count']].dropna()
    df_normal = df[(df['first_sorting_tm_c'] < datetime.datetime(2022, 3, 15)) | (
            df['first_sorting_tm_c'] >= datetime.datetime(2022, 5, 30))]
    df_normal = df_normal[['store_id_c', 'delv_center_num_c', 'lat', 'lng', 'sale_ord_count']].dropna()

    df_covid_counts = df_covid.groupby(['store_id_c', 'delv_center_num_c'])['sale_ord_count'].sum().reset_index(
        name='counts')
    df_normal_counts = df_normal.groupby(['store_id_c', 'delv_center_num_c'])['sale_ord_count'].sum().reset_index(
        name='counts')
    df_normal_counts = pandas.merge(addr_df, df_normal_counts, on=['store_id_c', 'delv_center_num_c'], how='right')
    df_covid_counts = pandas.merge(addr_df, df_covid_counts, on=['store_id_c', 'delv_center_num_c'], how='right')
    df_covid_counts.dropna(subset=['lat'], inplace=True)
    df_normal_counts.dropna(subset=['lat'], inplace=True)
    max_ = max(df_normal_counts['counts'].max(), df_covid_counts['counts'].max())
    df_normal_counts['weight'] = df_normal_counts['counts'] / max_
    df_covid_counts['weight'] = df_covid_counts['counts'] / max_

    normal_data = df_normal_counts[['lat', 'lng', 'weight']].values.tolist()
    covid_data = df_covid_counts[['lat', 'lng', 'weight']].values.tolist()
    gradient = {.2: "blue", .4: "cyan", .6: "lime", .8: "yellow", 1: "red"}
    map = folium.Map(location=[31.3004, 121.294], zoom_start=5)
    HeatMap(data=normal_data, gradient=gradient, radius=25, max_zoom=5, blur=10).add_to(map)
    map.save('htmls/common_warehouse_distribution_heatmap_waybill.html')
    map = folium.Map(location=[31.3004, 121.294], zoom_start=4)
    HeatMap(data=covid_data, gradient=gradient, radius=18, max_zoom=5, blur=10).add_to(map)
    map.save('htmls/covid_warehouse_distribution_heatmap_waybill.html')
    pass


def warehouse_distribution():
    df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/20220926_new/上海_1_8月_仓_出仓量_20220926212042.csv', engine='python',
        parse_dates=['first_sorting_tm_c'],
        skip_blank_lines=True)
    addr_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/仓_gps_营业部_polygon_/仓库地址坐标品类距离_v3.csv', engine='python',
        skip_blank_lines=True)

    addr_df = addr_df[['store_id_c', 'delv_center_num_c', 'lat', 'lng', 'city']].drop_duplicates()
    df = df[['first_sorting_tm_c', 'store_name_c', 'store_id_c', 'delv_center_num_c']]

    df = pandas.merge(df, addr_df, on=['store_id_c', 'delv_center_num_c'], how='left')

    # df_covid = df[(df['first_sorting_tm_c'] < datetime.datetime(2022, 7, 1)) & (
    #         df['first_sorting_tm_c'] >= datetime.datetime(2022, 3, 1))]
    # df_normal = df[(df['first_sorting_tm_c'] < datetime.datetime(2022, 3, 1)) | (
    #         df['first_sorting_tm_c'] >= datetime.datetime(2022, 7, 1))]
    df_covid = df[(df['first_sorting_tm_c'] < datetime.datetime(2022, 5, 30)) & (
            df['first_sorting_tm_c'] >= datetime.datetime(2022, 3, 15))]
    df_covid = df_covid[['store_id_c', 'delv_center_num_c', 'lat', 'lng']].drop_duplicates(
        subset=['lat', 'lng']).dropna()
    df_normal = df[(df['first_sorting_tm_c'] < datetime.datetime(2022, 3, 15)) | (
            df['first_sorting_tm_c'] >= datetime.datetime(2022, 5, 30))]
    df_normal = df_normal[['store_id_c', 'delv_center_num_c', 'lat', 'lng']].drop_duplicates(
        subset=['lat', 'lng']).dropna()
    df_normal['weight'] = 1
    df_covid['weight'] = 1

    normal_data = df_normal[['lat', 'lng', 'weight']].values.tolist()
    covid_data = df_covid[['lat', 'lng', 'weight']].values.tolist()
    gradient = {.2: "blue", .4: "cyan", .6: "lime", .8: "yellow", 1: "red"}
    map = folium.Map(location=[31.3004, 121.294], zoom_start=5)
    HeatMap(data=normal_data, gradient=gradient, radius=25, max_zoom=5, blur=10).add_to(map)
    map.save('htmls/common_warehouse_distribution_heatmap.html')
    map = folium.Map(location=[31.3004, 121.294], zoom_start=4)
    HeatMap(data=covid_data, gradient=gradient, radius=18, max_zoom=5, blur=10).add_to(map)
    map.save('htmls/covid_warehouse_distribution_heatmap.html')
    pass


def out_in():
    # first_sorting_tm_c,store_id_c,store_name_c,delv_center_num_c,delv_center_name_c,sale_ord_count
    out_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/20220926_new/上海_1_8月_仓_出仓量_20220926212042.csv', engine='python',
        parse_dates=['first_sorting_tm_c'],
        skip_blank_lines=True)
    # end_node_insp_tm_c,site_id_c,site_name_c,sale_ord_count
    in_df = pandas.read_csv(
        DISK_PATH_MACHINE + '数据/20220906/上海_1_8月_仓_入站量_20220906200142.csv', engine='python', encoding='gbk',
        parse_dates=['end_node_insp_tm_c'],
        skip_blank_lines=True)
    out_df = out_df[out_df['first_sorting_tm_c'] < datetime.datetime(2022, 7, 1)]
    in_df = in_df[in_df['end_node_insp_tm_c'] < datetime.datetime(2022, 7, 1)]
    out_df = out_df[out_df['first_sorting_tm_c'] >= datetime.datetime(2022, 3, 1)]
    in_df = in_df[in_df['end_node_insp_tm_c'] >= datetime.datetime(2022, 3, 1)]
    out_df['dt'] = out_df['first_sorting_tm_c'].dt.strftime('%m-%d')
    in_df['dt'] = in_df['end_node_insp_tm_c'].dt.strftime('%m-%d')
    out_df['id'] = out_df.groupby(['store_id_c', 'delv_center_num_c']).ngroup()
    df_res_out = out_df.groupby(['dt', 'id'])[
        'sale_ord_count'].sum().unstack(
        fill_value=0)
    df_res_out["res"] = df_res_out.apply(lambda x: x.sum(), axis=1)
    df_res_in = in_df.groupby(['dt', 'site_id_c'])['sale_ord_count'].sum().unstack(
        fill_value=0)
    df_res_in["res"] = df_res_in.apply(lambda x: x.sum(), axis=1)
    df_res_in.reset_index(inplace=True)
    df_res_out.reset_index(inplace=True)
    df_res_in = df_res_in[['dt', 'res']]
    df_res_out = df_res_out[['dt', 'res']]
    df_res_in['type'] = '入站量'
    df_res_out['type'] = '出仓量'
    df_res = pandas.concat([df_res_out, df_res_in], axis=0).sort_values(by='dt', ascending=True)
    df_res.to_csv('csvs/入站量—出仓量-2022-3-7.csv', index=False)
    import seaborn as sns
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    ax = sns.lineplot(x='dt', y='res', hue='type', data=df_res, palette=['#D98880', '#7DCEA0'])
    ax.xaxis.set_major_locator(MultipleLocator(15))
    ax.grid(True)  # 显示网格
    plt.ylabel('单量', fontsize=15)
    ax.legend_.set_title(None)
    plt.xlabel('日期', fontsize=15)
    ax.set_title('上海市3～7月订单的出仓量和入站量', fontsize=18)
    plt.savefig('pngs/上海市3-7月订单的出仓量和入站量.png')
    plt.show()
    pass


if __name__ == '__main__':
    warehouse_waybill_distribution()

    # out_in()
