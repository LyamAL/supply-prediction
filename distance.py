import pandas as pd
import torch

import util

if __name__ == '__main__':
    site_df = pd.read_csv('F:\myStuff\数据\仓_gps_营业部_polygon_\上海营业站位置信息with合并围栏.csv', engine='python',
                          skip_blank_lines=True)
    site_df.sort_values(by=['site_code'], ascending=True, inplace=True, ignore_index=False)
    site_df_db = site_df
    dis_matrix = torch.zeros(site_df.shape[0], site_df.shape[0])

    site_df = site_df[['site_code', 'lng_new', 'lat_new']]
    for index, row in site_df_db.iterrows():
        for i, r in site_df.iterrows():
            dis = util.distance((r['lat_new'], r['lng_new']), (row['lat_new'], row['lng_new']))
            dis_matrix[index, i] = dis

    print(dis_matrix)
    torch.save(dis_matrix, 'F:\myStuff\数据\仓_gps_营业部_polygon_\distance_between_sites.pt')
