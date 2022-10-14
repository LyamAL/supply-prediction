import re

import pandas



# 哈尔滨 石家庄 驻马店 中国澳门 乌鲁木齐 呼和浩特
def getStrictType(x):
    # if 'FDC' in x:
    #     return 'FDC', 'FDC'
    # if '平台' in x:
    #     return '公共平台', '公共平台'
    if '服' in x:
        if '饰' in x:
            return '服饰', '服饰'
        return '服饰', '服装'
    # if '蕉内' in x:
    #     return '服饰', '服装'
    # if '布衣' in x:
    #     return '服饰', '服装'
    # if '丽歌' in x:
    #     return '服饰', '服饰'
    # if '七匹狼' in x:
    #     return '服饰', '服饰'
    # if '稻草人' in x:
    #     return '服饰', '服饰'
    # if '诺奇' in x:
    #     return '服饰', '服饰'
    # if '卓伊' in x:
    #     return '服饰', '服饰'
    # if '唐狮' in x:
    #     return '服饰', '服饰'
    # if '立酷派' in x:
    #     return '服饰', '服饰'
    # if '骏方' in x:
    #     return '医药保健', '医疗器械'
    # if '汤臣倍健' in x:
    #     return '医药保健', '保健品'
    # if '朗德万斯' in x:
    #     return '家居日用', '家具建材'
    # if '耐朴' in x:
    #     return '家居日用', '家居日用'
    # if '一免' in x:
    #     return '母婴玩具', '母婴玩具'
    # if '千里马' in x:
    #     return '汽车用品', '汽车用品'

    if '医疗器械' in x:
        return '医药保健', '医疗器械'

    if '药' in x:
        return '医药保健', '中西药品'
    if '书' in x:
        return '图书音像', '图书'
    if '家居日用' in x:
        return '家居日用', '家居日用'
    if '母婴玩具' in x:
        return '母婴玩具', '母婴玩具'
    if '家具建材' in x:
        return '家居日用', '家具建材'
    if '米面粮油' in x:
        return '食品酒类', '米面粮油'
    if '牛奶水饮' in x:
        return '食品酒类', '饮料冲调'
    if '休闲食品' in x:
        return '食品酒类', '休闲食品'
    if '生鲜' in x:
        return '食品酒类', '水果生鲜'
    if '个护清洁' in x:
        return '个护清洁', '个护清洁'
    if '宠' in x:
        return '宠物', '宠物园艺'
    if '酒' in x:
        return '食品酒类', '酒类'
    if '家纺' in x:
        return '家居家装', '家纺'
    if '汽' in x:
        if '旅' in x:
            return '汽车用品', '车旅用品'
        return '汽车用品', '汽车用品'
    if '3C' in x:
        detail = ['通讯', '电脑办公', '零售']
        for t in detail:
            if t in x:
                if t == '通讯':
                    return '3C', '数码通讯'
                return '3C', t
        return '3C', '3C'

    # ghqj = ['金红叶', '洁柔', '维达', '金佰利', '曼伦', '隆力奇'
    #                                         '滴露', '蓝月亮', '宝洁', '雅芳', '戴森', '植物医生', '立白']
    # xxsp = ['品利', '雀巢', '周黑鸭', '万佳宏业']
    # nnsy = ['农夫山泉', '蒙牛', '伊利']
    # xbxxss = ['安踏', '特步', '361度', '斯凯奇', '李宁', '迪卡侬', '斐乐', '鸿星尔克', '意尔康', '普利达斯', '古奇天伦云仓1']
    # sjsm = ['电信', '移动', '腾讯', '荣耀', '小米', '新通路']
    # jiu = ['茅台', '酒']
    # for q in ghqj:
    #     if q in x:
    #         return '个护清洁', '个护清洁'
    # for q in xxsp:
    #     if q in x:
    #         return '食品酒类', '休闲食品'
    # for q in nnsy:
    #     if q in x:
    #         return '食品酒类', '饮料冲调'
    # for q in xbxxss:
    #     if q in x:
    #         return '箱包鞋靴', '流行鞋服'
    # for q in sjsm:
    #     if q in x:
    #         return '手机/运营商/数码', '手机/运营商/数码'
    # for q in jiu:
    #     if q in x:
    #         return '食品酒类', '酒类'
    # if '乐创' in x:
    #     return '家用电器', '家用电器'
    # if '美的' in x:
    #     return '家用电器', '生活小电'
    # if '史密斯' in x:
    #     return '家用电器', '厨卫大电'
    # if '无印良品' in x:
    #     return '家居日用', '家居日用'

    if '生活小电' in x:
        return '家用电器', '生活小电'
    if '厨房小电' in x:
        return '家用电器', '厨房小电'
    # if '综合' in x or '沃尔玛' in x:
    #     return '综合', '综合'
    if '冷链' in x:
        return '冷链', '冷链'
    # if '消费品' in x:
    #     return '消费品', '消费品'
    if '商超' in x or '百货' in x:
        return '商超百货', '商超百货'
    # if '本地仓' in x:
    #     return '本地仓', '本地仓'
    # if '云仓' in x:
    #     return '云仓', None
    # if '共享仓' in x:
    #     return '共享仓', '共享仓'
    return '其他', '其他'


ls = ['FDC', '新通路', '综合']
ls2 = ['商超', '小电', '药品', '百货', '3C', '健康', '服装', '图书', '生鲜', '冷链', '零售']


def merge(st):
    for t in ls:
        if t in st:
            return t
    st = st.replace('A', '')
    st = st.replace('B', '')
    for t in ls2:
        if t in st:
            return t
    return '其他'


def extractType(df):
    # re.match('(.{2}[滨庄店澳门木齐浩特]{1,2})(.+仓).*号?库?.*', '上海3CA通讯专用仓1号库')
    df[['city', 'type']] = df['store_name_c'].str.extract('(.{2}[滨庄店澳门木齐浩特哈尔]{0,2})(.+仓).*号?库?.*',
                                                          expand=True)
    df[['type', 'sub_type']] = df.apply(lambda x: getStrictType(x['store_name_c']), axis=1,
                                        result_type="expand")
    df = df[df['type'] != '其他']
    df_nan = df[df[['type']].isnull().T.any()]
    print('可用仓', len(df['store_name_c'].value_counts()), '个')


def mergeType(df):
    df['storetype'] = df['storetype'].apply(lambda x: merge(x))
    return df


if __name__ == '__main__':
    df_warehouse = pandas.read_csv('F:/myStuff/数据/仓_gps_营业部_polygon_/warehouse_address.csv', engine='python',
                                   skip_blank_lines=True)
    df_warehouse.drop('Unnamed: 0', inplace=True, axis=1)
    df_warehouse = df_warehouse[
        ['store_id_c', 'delv_center_num_c', 'store_name_c', 'delv_center_name_c', 'address', 'lat', 'lng', 'storetype']]
    df_warehouse.dropna(subset=['store_name_c'], inplace=True)
    df_warehouse.dropna(subset=['address'], inplace=True)
    print('共有仓', len(df_warehouse['store_name_c'].value_counts()), '个')
    # 我的分类
    # extractType(df_warehouse)
    # 已有分类
    df_warehouse = mergeType(df_warehouse)
    print('可用仓', len(df_warehouse['store_name_c'].value_counts()), '个')
    df_warehouse.to_csv('F:\myStuff\数据\仓_gps_营业部_polygon_\仓库地址坐标品类_new.csv', index=False)
