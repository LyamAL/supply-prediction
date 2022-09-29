import re

import pandas

if __name__ == '__main__':
    df = pandas.read_csv('F:\myStuff\数据\\20220906\仓_上海_1月_8月仓至站数据_20220908191143.csv', engine='python',
                         skip_blank_lines=True)
    df.drop('store_id_c', inplace=True, axis=1)
    df_u = df.drop_duplicates(subset=['store_name_c'])
    df_u = df_u.reset_index()
    df_u['warehouse_id'] = range(len(df_u))
    df_u = df_u[['warehouse_id', 'store_name_c']]
    df = pandas.merge(df, df_u, on='store_name_c', how='left')
    df.to_csv('F:\myStuff\数据\\模拟数据\仓_上海_1月_8月仓至站数据_.csv',index=False)
    print(df_u.shape[0])
