import pickle
import re

import pandas


def AddEdge(data, nodeName):
    nodeAdded = 0
    for tpl in data:
        if nodeName == tpl[0]:
            tpl[1] += 1
            nodeAdded = 1
            break
    if not nodeAdded:
        data.append([nodeName, 1])
    return data


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# 有单量/地址的站 280+
def filter_sites(df):
    site_df_all = pandas.read_csv(
        'site_features_covid.csv',
        engine='python',
        skip_blank_lines=True)
    df = df[df['end_node_name'].isin(site_df_all['node_name'].tolist())]
    return df


# 有单量/地址/品类的仓库 789个
def filter_warehouses(df):
    warehouse_df_all = pandas.read_csv(
        'warehouse_features_v3.csv',
        engine='python',
        skip_blank_lines=True)
    df = df[df['start_node_name'].isin(warehouse_df_all['store_name_c'].tolist())]
    return df


'''
输入：csv路径：需要字段'real_delv_tm', 'start_node_name', 'recommended_routing', 'end_node_name', 'start_opt_tm'
输出：pkl文件结构：list->dict->list，第一个list为每14天数据；第二个dict为单14天中的结点（key）和该节点的邻居信息（list）；最后一个list就是邻居信息[结点名称，单量数量]
示例：
[
    [ 
        {'a仓':
            [
                [a分拣中心,2],
                [p站,1]
            ]
        },
        {'b仓':
            [
                [b分拣中心,2],
                [c站,1]
            ]
        }
    ]
]
'''


def get_graph_dict(path):
    df = pandas.read_csv(
        path,
        parse_dates=['real_delv_tm', 'start_opt_tm'],
        engine='python', skip_blank_lines=True)

    df.dropna(subset=['real_delv_tm'], inplace=True)
    df.dropna(subset=['recommended_routing'], inplace=True)
    df.dropna(subset=['start_opt_tm'], inplace=True)
    df = df[['start_node_name', 'recommended_routing', 'end_node_name', 'start_opt_tm']].drop_duplicates()
    df = filter_warehouses(df)
    df = filter_sites(df)

    date_list = pandas.date_range(start=df['start_opt_tm'].min(), end=df['start_opt_tm'].max()).to_pydatetime().tolist()
    dates_interval = list(chunks(date_list, 14))
    res_dict = dict()
    res_list = list()
    for idx, interval in enumerate(dates_interval):
        df_ = df[(df['start_opt_tm'].isin(interval))]
        dfg_ = df_.groupby('start_node_name')
        for warehouse_nm, group in dfg_:
            # 第一个分拣中心是仓的邻居，最后一个分拣中心是站的邻居，分拣中心和分拣中心之间互为邻居
            warehouse_data = res_dict[warehouse_nm] if warehouse_nm in res_dict else list()
            for idx, row in group.iterrows():
                re_center = re.compile('([\u4e00-\u9fa5]+分拣中心)')
                center_list = re_center.findall(row['recommended_routing'])
                site_nm = row['end_node_name']

                if len(center_list) == 0:
                    warehouse_data = AddEdge(warehouse_data, site_nm)
                    # 站的聚合
                    site_data = res_dict[site_nm] if site_nm in res_dict else list()
                    site_data = AddEdge(site_data, warehouse_nm)
                    res_dict[site_nm] = site_data
                    continue

                first_center = center_list[0]
                last_center = center_list[-1]
                warehouse_data = AddEdge(warehouse_data, first_center)
                # 站的聚合
                site_data = res_dict[site_nm] if site_nm in res_dict else list()
                site_data = AddEdge(site_data, last_center)
                res_dict[site_nm] = site_data
                # 分拣中心的聚合：前后节点
                for i, center_nm in enumerate(center_list):
                    cur_center_data = res_dict[center_nm] if center_nm in res_dict else list()
                    if i == 0:
                        cur_center_data = AddEdge(cur_center_data, warehouse_nm)
                    else:
                        cur_center_data = AddEdge(cur_center_data, center_list[i - 1])
                    if i + 1 == len(center_list):
                        cur_center_data = AddEdge(cur_center_data, site_nm)
                    else:
                        cur_center_data = AddEdge(cur_center_data, center_list[i + 1])
                    res_dict[center_nm] = cur_center_data

            res_dict[warehouse_nm] = warehouse_data

        res_list.append(res_dict)
        res_dict = dict()
    with open('heterogeneous_relation.pkl', 'wb') as f:
        pickle.dump(res_list, f)
