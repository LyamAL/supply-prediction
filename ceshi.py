import pandas

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
    draw()
