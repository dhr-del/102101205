import csv
import datetime
import re
import time
from collections import Counter
import jieba
import pandas as pd
import requests
import wordcloud
from msedge.selenium_tools import EdgeOptions, Edge

# 开始时间
# start_time = time.time()


#函数
def get_bv(urls):
    sum_bv = []
    # 配置Microsoft Edge浏览器的驱动路径
    driver_path = 'D:\Download\AppGallery\python\MicrosoftWebDriver.exe'

    # 创建Microsoft Edge浏览器的选项
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    edge_options.add_argument('--headless')  # 无头模式

    # 创建Microsoft Edge浏览器驱动
    driver = Edge(executable_path=driver_path, options=edge_options)
    for url in urls:
        # 打开网页
        driver.get(url)

        # 等待页面加载完全
        time.sleep(3)

        # 获取页面源代码
        html = driver.page_source

        per_bv = re.findall(r'(BV.{10})', html)
        # 去重
        for a in per_bv:
                sum_bv.append(a)

    # 关闭浏览器驱动
    driver.quit()

    return sum_bv

def get_dm_url(bv):
    # 构造弹幕请求地址
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bv}'

    # 发送请求并获取视频信息
    response = requests.get(url)
    data = response.json()

    # 提取视频的弹幕 oid
    oid = data['data']['cid']

    # 构造弹幕地址
    dm_url = f'https://api.bilibili.com/x/v1/dm/list.so?oid={oid}'

    return dm_url
def getdanmu(video_urls):
#创建文件
 f = open('弹幕数据.csv', mode='w', encoding='utf-8', newline='')
 csv_writer = csv.DictWriter(f, fieldnames=['弹幕时间', '弹幕内容'])
 csv_writer.writeheader()

 # 循环遍历每个视频URL
 for i, url in enumerate(video_urls):
    # 发送请求
    response = requests.get(url)
    response.encoding = 'utf-8'

    # 解析数据
    info_list = re.findall('<d p="(.*?)">(.*?)</d>', response.text)

    # 保存弹幕数据到CSV文件
    for info, content in info_list:
        send_time = info.split(',')[4]
        time = datetime.datetime.fromtimestamp(int(send_time))
        time = time.strftime('%Y-%m-%d %H:%M:%S')
        dit = {'弹幕时间': time, '弹幕内容': content}
        csv_writer.writerow(dit)
        # print(dit)

 f.close()
def ciyunzhizuo():
  getdanmu(real_oid)
  # 读取数据
  df = pd.read_csv('弹幕数据.csv')
  # 获取弹幕内容 列表推导式
  content_list = [i for i in df['弹幕内容']] #把弹幕内容弄成一个列表
  # 列表合并成字符串
  content = ' '.join(content_list)#content_list列表中的所有元素连接在一起成为一个字符串，每个元素用空格隔开

  # 生成词云图
  txt = jieba.lcut(content)# 结巴分词 #对 content 进行分词，将分词结果存储在 txt 变量中,每个分词有一个单引号
  string = ' '.join(txt)# 列表合并成字符串 #使用空格将列表 txt 中的所有分词连接成一个字符串，每个分词用空格隔开#使用空格将列表 txt 中的所有分词连接成一个字符串，每个分词用空格隔开

  wc = wordcloud.WordCloud(height=700, width=1000, background_color='pink', font_path='msyh.ttc',
                         stopwords={'了', '我', '的', '的', '是', '吗', '我', '啊', '有', '都', '你', '他','他们'})#排除一些文字
  wc.generate(string)#输入词云图所需数据
  wc.to_file('词云图.png')

  # print(string)
def get_top_elements(lst, n):
    count = Counter(lst)
    top_elements = count.most_common(n)
    return top_elements


# 获取链接列表
urls=["https://search.bilibili.com/all?keyword=%E6%97%A5%E6%9C%AC%E6%A0%B8%E6%B1%A1%E6%9F%93%E6%B0%B4%E6%8E%92%E6%B5%B7&from_source=webtop_search&spm_id_from=333.1007&search_source=5"]
for i in range(2,10):
    url= f"https://search.bilibili.com/all?keyword=%E6%97%A5%E6%9C%AC%E6%A0%B8%E6%B1%A1%E6%9F%93%E6%B0%B4%E6%8E%92%E6%B5%B7&from_source=webtop_search&spm_id_from=333.1007&search_source=5&page={i}&o={30 * (i-1)}"
    urls.append(url)
#函数1
bvs = get_bv(urls)
# 去重
real_bv=[]
for a in bvs:
    if real_bv.count(a)== 0:
        real_bv.append(a)
real_oid=[]

#函数2
for bv in real_bv:
   dm_url = get_dm_url(bv)
   real_oid.append(dm_url)
# print(real_oid)
print(len(real_oid))

#函数3
getdanmu(real_oid)

#函数4
ciyunzhizuo()

# 读取数据
df = pd.read_csv('弹幕数据.csv')
df.to_excel('弹幕数据.xlsx', index=False)
# 获取弹幕内容
content_list = df['弹幕内容'].tolist()

#函数5
result = get_top_elements(content_list, 20)
print(result)

#存入文件
filename = '前20个出现次数最多的弹幕.csv'
with open(filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['编号', '弹幕内容', '数量'])

    for i, item in enumerate(result, start=1):
        writer.writerow([i, item[0], item[1]])

df = pd.read_csv('前20个出现次数最多的弹幕.csv')
df.to_excel('前20个出现次数最多的弹幕.xlsx', index=False)

# end_time = time.time()
# execution_time = end_time - start_time
# print("代码执行时间：", execution_time)