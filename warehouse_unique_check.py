import pandas as pd

if __name__ == '__main__':

    type_df = pd.read_csv('F:/myStuff/数据/仓_gps_营业部_polygon_/warehouse_type_new.csv', engine='python',
                          skip_blank_lines=True)
    # warehouse_df = pd.read_csv('F:/myStuff/数据/仓_gps_营业部_polygon_/仓库信息.csv', engine='python',
    #                            skip_blank_lines=True)
    # warehouse_type_df = pd.merge(warehouse_df, type_df, on='store_name_c', how='right')

    # addr_df = pd.read_csv('F:/myStuff/数据/仓_gps_营业部_polygon_/仓地址_771.csv', engine='python',
    #                       skip_blank_lines=True)
    addr_df = pd.read_csv('F:/myStuff/数据/仓_gps_营业部_polygon_/warehouse_address.csv', engine='python',
                          skip_blank_lines=True)
    addr_df.drop('Unnamed: 0', inplace=True, axis=1)
    addr_df.drop_duplicates(subset=['addr'], inplace=True)
    warehouse_addr_type_df = pd.merge(warehouse_type_df, addr_df, on='store_name_c', how='left')
    
    warehouse_addr_type_df_nan = warehouse_addr_type_df[warehouse_addr_type_df[['addr']].isnull().T.any()]
    warehouse_addr_type_df_nan = warehouse_addr_type_df_nan[['store_name_c', 'store_id_c']]
    
    warehouse_addr_type_df_nan.to_csv('F:/myStuff/数据/仓_gps_营业部_polygon_/缺地址仓.csv', index=False)
    pass

    # res = warehouse_type_df.value_counts('type').to_dict()
    # keys = list(res.keys())
    # # get values in the same order as keys, and parse percentage values
    # vals = [float(res[k]) for k in keys]
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    # plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # plt.figure(figsize=(12, 8))
    # sns.barplot(x=keys, y=vals)
    # plt.xlabel('仓类别')
    # plt.ylabel('仓数量占比')
    # plt.title('同类仓数量')
    # plt.savefig('F:/myStuff/数据/分析/仓/同类仓数量.png')
    # plt.show()

    # warehouse_out_df.drop('store_id_c', inplace=True, axis=1)
    # warehouse_out_df_type = pd.merge(warehouse_out_df, warehouse_type_df, on='store_name_c', how='left')
    # warehouse_out_df_type = warehouse_out_df_type[warehouse_out_df_type['type'] != '其他']
    # warehouse_out_df_type.dropna(subset=['type'], inplace=True)
    # gb_result = warehouse_out_df_type.groupby(['first_sorting_tm_c', 'type'])
    # # gb_result = warehouse_out_df_type.groupby(['first_sorting_tm_c'], ['type'])['sale_ord_count']
    #
    # for g, v in gb_result:
    #     print(g)
    #     print(v)
