import requests
import pandas as pd
import datetime
import os
import re

# 获取今天的日期
today = datetime.datetime.now().strftime('%Y-%m-%d')

# 获取昨天的日期
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# 获取最近的一个文件日期
files = os.listdir('.')
recent_files = [file for file in files if file.startswith('byd_join_shop_') and not 'diff' in file and file.endswith('.csv')]
if recent_files:
    recent_file = max(recent_files, key=lambda x: datetime.datetime.strptime(re.findall(r'\d{4}-\d{2}-\d{2}', x)[0], '%Y-%m-%d'))
else:
    recent_file = None


# 获取今天的加盟店信息
url_today = 'https://www.bydauto.com.cn/api/comom/search_join_shop'
params_today = {
    'page': 1,
    'pageSize': 10000,
    'provinceCode': '',
    'cityCode': '',
    'countyCode': '',
    'shopName': '',
    'shopType': '',
    'shopLevel': '',
    'shopStatus': '',
    'longitude': '',
    'latitude': ''
}
response_today = requests.post(url_today, json=params_today)
data_today = response_today.json()['data']
df_today = pd.DataFrame(data_today)

# 将今天的加盟店信息保存到csv文件中
filename_today = f'byd_join_shop_{today}.csv'
df_today.to_csv(filename_today, index=False)

# 对比两个文件中第二列的数据，筛选出新增和减少的经销商名称
if recent_file is not None:
    filename_yesterday = recent_file
    try:
        df_yesterday = pd.read_csv(filename_yesterday)
        print(f'对比文件1: {filename_yesterday}')
        print(f'对比文件2: {filename_today}')
    except FileNotFoundError:
        print(f'{filename_yesterday} 文件不存在')
        df_yesterday = pd.DataFrame()
else:
    print('没有找到之前的数据文件')
    df_yesterday = pd.DataFrame()

if df_yesterday.empty:
    diff_add = df_today.copy()
    diff_del = pd.DataFrame()
else:
    diff_add = df_today[~df_today.iloc[:, 1].isin(df_yesterday.iloc[:, 1])]
    diff_del = df_yesterday[~df_yesterday.iloc[:, 1].isin(df_today.iloc[:, 1])]

# 将新增和减少的经销商名称保存到新的csv文件中
filename_diff = f'byd_join_shop_diff_{today}.csv'
with open(filename_diff, mode='w', encoding='utf-8') as f:
    f.write('新增经销商名称\n')
    f.write(diff_add.iloc[:, 1].to_csv(index=False))
    f.write('\n减少经销商名称\n')
    f.write(diff_del.iloc[:, 1].to_csv(index=False))
