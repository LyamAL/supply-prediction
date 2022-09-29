import pandas

import util

if __name__ == '__main__':

    covid_df = pandas.read_csv('F:\myStuff\数据\疫情数据\上海疫情_20220911183542.csv', engine='python', skip_blank_lines=True)
    covid_df_valid = covid_df[covid_df['lat'] != 0.0]
    covid_df_invalid = covid_df[covid_df['lat'] == 0.0]
    print(covid_df_valid.shape[0] / covid_df.shape[0])
    # 解析gps
    covid_df['subdivision'] = covid_df['subdivision'].str.replace('?', '', regex=False)
    covid_df['subdivision'] = covid_df['subdivision'].str.replace('（', '(', regex=False)
    covid_df['subdivision'] = covid_df['subdivision'].str.replace('）', ')', regex=False)
    covid_df_invalid[['lng', 'lat']] = covid_df_invalid.apply(
        lambda x: util.geocodeB(x['city'] + x['county'] + x['town'] + x['subdivision'][5:9]), axis=1, result_type="expand")

    # 现将表构成list，然后在作为concat的输入
    frames = [covid_df_valid, covid_df_invalid]

    covid_df_all = pandas.concat(frames)
    covid_df_all.to_csv('covid_with_gps.csv', index=False)
