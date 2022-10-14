import datetime
import os

import numpy as np
import pandas
import plotly.graph_objects as go


# noinspection PyTypeChecker
def DrawSankey(res, ymd, site_df):
    if res.shape[0] == 0:
        return
    res['sh'] = res.apply(lambda x: 1 if x['city'] == '上海市' else 0, axis=1)
    res.sort_values(by='sh', ascending=False, inplace=True)
    warehouse_range = res['city'].value_counts().sort_index().index.tolist()
    warehouse_map = dict(zip(warehouse_range, list(range(len(warehouse_range)))))
    res['city_id'] = res['city'].map(warehouse_map)

    site_df['site_id'] = site_df.index + res['city_id'].max() + 1
    res = pandas.merge(res, site_df, on='site_name_c', how='left')  # get site node indices
    store_label_list = np.array(res.drop_duplicates(subset='city_id')['city']).tolist()
    node_labels_list = store_label_list + list(site_df['site_name_c'])  # node labels
    idx = 0
    colors = len(store_label_list) * ['']
    for i in node_labels_list:
        if idx == len(store_label_list): break
        colors[idx] = 'green' if i == '上海市' else 'blue'
        idx += 1

    node = dict(
        pad=10,
        label=node_labels_list,
        color=colors
    )
    source_list = list(res['city_id'])
    target_list = list(res['site_id'])
    value_list = np.array(res['sale_ord_count']).tolist()
    LINKS = dict(
        source=source_list,  # 链接的起点或源节点
        target=target_list,  # 链接的目的地或目标节点
        value=value_list)
    data = go.Sankey(node=node, link=LINKS)
    fig = go.Figure(data)
    fig.update_layout(title_text="{dt}".format(dt=ymd), font_size=10)
    newpath = r'pngs/'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    fig.write_image("pngs/{dt}.png".format(dt=ymd))


def arrangeData():
    warehouse_info_df = pandas.read_csv('/Users/lyam/同步空间/数据/仓/warehouse_features_v2.csv', engine='python',
                                        skip_blank_lines=True)
    warehouse_info_df = warehouse_info_df[['store_id_c', 'delv_center_num_c', 'city']]
    ws_df = pandas.read_csv('/Users/lyam/同步空间/仓_入站量/00_xkw_仓_上海_1月_8月仓至站数据_20221007000922.csv',
                            encoding='gbk',
                            engine='python', parse_dates=['first_sorting_tm_c'], skip_blank_lines=True)
    ws_df = ws_df[ws_df['site_id_c'] == 1168]
    ws_df = ws_df[
        ['first_sorting_tm_c', 'store_id_c', 'delv_center_num_c', 'store_name_c', 'site_id_c', 'sale_ord_count']]
    start_date = datetime.datetime(2022, 1, 1, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 8, 15, hour=0, minute=0, second=0)
    cur_date = start_date
    df_res = pandas.DataFrame(
        columns=['site_id_c', 'sale_ord_count', 'store_name_c', 'city',
                 'first_sorting_tm_c'])
    # 是否有单量
    while cur_date <= end_date:
        tomorrow = cur_date + datetime.timedelta(days=1)
        ware_to_site_daily_df = ws_df[
            (ws_df['first_sorting_tm_c'] >= cur_date) & (ws_df['first_sorting_tm_c'] < tomorrow)]
        ware_to_site_daily_df = pandas.merge(ware_to_site_daily_df, warehouse_info_df,
                                             on=['store_id_c', 'delv_center_num_c'], how='inner')
        ware_to_site_daily_df.drop('delv_center_num_c', inplace=True, axis=1)
        ware_to_site_daily_df.drop('store_id_c', inplace=True, axis=1)
        dfg = ware_to_site_daily_df.groupby(['city', 'site_id_c'])
        for k, v in dfg:
            if v.shape[0] <= 1:
                df_res = pandas.concat([df_res, v])
            else:
                fr = v.iloc[0]
                fr['sale_ord_count'] = v['sale_ord_count'].sum()
                fr = fr.to_dict()
                df_res = pandas.concat([df_res, pandas.DataFrame([fr])])
                pass
        cur_date = tomorrow

    df_res.to_csv('/Users/lyam/同步空间/temp/city-site_qty.csv', index=False)  # 一个营业站的8个月数据
    # 有数据后从这里开始直接读
    # df_res = pandas.read_csv('/Users/lyam/同步空间/temp/city-site_qty.csv',
    #                          engine='python', parse_dates=['first_sorting_tm_c'], skip_blank_lines=True)

    site_df = pandas.read_csv('/Users/lyam/同步空间/数据/营业站/available_sites_with_fences_v2.csv', engine='python',
                              skip_blank_lines=True)
    site_df = site_df[['site_id_c', 'site_name_c']]
    df_res = pandas.merge(df_res, site_df, on='site_id_c', how='left')  # 获得site name
    start_date = datetime.datetime(2022, 1, 1, hour=0, minute=0, second=0)
    end_date = datetime.datetime(2022, 8, 15, hour=0, minute=0, second=0)
    cur_date = start_date
    while cur_date <= end_date:
        ymd = cur_date.strftime("%m-%d")
        tomorrow = cur_date + datetime.timedelta(days=1)
        df_daily = df_res[
            (df_res['first_sorting_tm_c'] >= cur_date) & (df_res['first_sorting_tm_c'] < tomorrow)]
        DrawSankey(df_daily, ymd, site_df[['site_name_c']])
        cur_date = tomorrow


if __name__ == '__main__':
    arrangeData()
