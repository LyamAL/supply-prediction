import folium
import pandas

from features_construction import toGeoFence

map = folium.Map(location=[31.3004, 121.294], zoom_start=10)
if __name__ == '__main__':
    site_relations_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/site_relations_01_matrix.csv',
        engine='python',
        skip_blank_lines=True)
    site_fence_df = pandas.read_csv(
        '/Users/lyam/同步空间/数据/营业站/available_sites_with_fences.csv',
        engine='python',
        skip_blank_lines=True)
    site_fence_df = toGeoFence(site_fence_df, 'fence')
    for idx in range(0, 285):
        for i in range(0, 285):
            if idx == i:
                continue
            poly1 = site_fence_df[site_fence_df.iloc[idx]]['fence']
            poly2 = site_fence_df[site_fence_df.iloc[i]]['fence']
            # 画polygon
            fillColor = 'green'
            color = 'white'
            polyg1_ = folium.GeoJson(
                poly1,
                style_function=lambda x, fillColor=fillColor, color=color: {
                    "fillColor": fillColor,
                    "color": color,
                    'weight': 1,
                    'fillOpacity': 0.5},
            )
            polyg2_ = folium.GeoJson(
                poly2,
                style_function=lambda x, fillColor=fillColor, color=color: {
                    "fillColor": fillColor,
                    "color": color,
                    'weight': 1,
                    'fillOpacity': 0.5},
            )
            polyg1_.add_to(map)
            polyg2_.add_to(map)
            map.fit_bounds(map.get_bounds(), padding=(10, 10))
            map.save('checkNeighbors.html')
