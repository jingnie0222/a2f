#WAP新闻类型的监控
from pyppeteer import launch
import time
import datetime
import requests 
import PuppeteerActions as ppa
import asyncio
import DataFile
import Template
import xml.etree.ElementTree as ET
import urllib

#设置一些常量
#expire_timestamp_limit = 432000 #设置5天之前的算是时效性差
expire_timestamp_limit = 86400 #DEBUG 1天之前的都算有问题
reports = Template.ReportData('新闻时效性专项监控', ["查询词", "标题", "第N条", "时间"])
maillist = 'fanghuizhi@sogou-inc.com;'

#读取词表
wordlist = []
rs = requests.get('https://m.sogou.com/reventondc/wireless')
root = ET.fromstring(rs.text)
news_node = root.find("item").find("display").find("list")
for node in news_node.findall("form"):
    #wordlist.append( "http://m.sogou.com.inner/web/searchList.jsp?keyword=" + urllib.parse.quote(node.find("newsTitle").text))
    wordlist.append(node.find("newsTitle").text)
    
async def verify_news(words):
    in_data = []
    news_times_data = []
    wx_times_data = []
    curr_timestamp = time.time()
    browser = await launch({"executablePath": "chromium-browser", "args": ["--no-sandbox"]})
    page = await browser.newPage()
    for word in words:
        url = "http://m.sogou.com.inner/web/searchList.jsp?keyword=" + urllib.parse.quote(word)
        print ("fetching " + url)
        await page.goto(url)
        news_times_data_tmp = await get_news_times(page, word)
        news_times_data = news_times_data + news_times_data_tmp
        wx_times_data_tmp = await get_weixin_times(page, word)
        wx_times_data = wx_times_data + wx_times_data_tmp
    await browser.close()
    
    #输出报告
    report_header = ["QUERY", "序号", "标题", "类型", "更新时间"]
    report_content = "".join([Template.html_general_css(), Template.html_h3_title("新闻类时效性"), Template.html_table(turn_cluster_data_to_list(news_times_data), report_header), Template.html_h3_title("微信类时效性"), Template.html_table(turn_cluster_data_to_list(wx_times_data), report_header)])
    DataFile.write_full_file("data/tmp/news.html", report_content)
    
async def get_news_times(page, word):
    vrpath_news = await ppa.combo_wap_get_vrid(page, '30000501')
    if(vrpath_news is None):
        return []
    print ("news" + vrpath_news)
    times_arr = await ppa.action_get_elements_content(page, vrpath_news + " time")
    titles_arr = await ppa.action_get_elements_content(page, vrpath_news + " h4[class='clamp2']")
    final_data = mix_cluster_data(word, times_arr, titles_arr, "新闻")
    return final_data
    
async def get_weixin_times(page, word):
    vrpath_wx = await ppa.combo_wap_get_vrid(page, '11002501')
    if(vrpath_wx is None):
        return []
    print ("wx " + vrpath_wx)
    times_arr = await ppa.action_get_elements_content(page, vrpath_wx + " span[class*='timechange']")
    titles_arr_1 = await  ppa.action_get_elements_content(page, vrpath_wx + " p[class='space-txt wd-title']")
    titles_arr_2 = await  ppa.action_get_elements_content(page, vrpath_wx + " h4[class='article-title wd-title']")
    titles_arr = titles_arr_1 + titles_arr_2
    final_data = mix_cluster_data(word, times_arr, titles_arr, "微信")
    return final_data
    
#把mix_cluster_data返回的数据从dict转化为list供展示
def turn_cluster_data_to_list(in_data):
    ret_data = []
    for row in in_data:
        ret_data.append([row['query'], row['order'], row['title'], row['type'], row['time']])
    return ret_data

#把time和title标签的数组混合起来，返回字典组成的list，每条对应一个字典
def mix_cluster_data(query, times_arr, titles_arr, type):
    ret_data = []
    if(not len(times_arr) == len(titles_arr)):
        print ("WARNING times:" + str(len(times_arr)) + ", titles:" + str(len(titles_arr)))
        return ret_data
    order = 0
    for title in titles_arr:
        ret_data.append({"query" :query, "order" : str(order + 1) , "title" : title, "type" : type, "time" : times_arr[order]})
        order = order + 1
    return ret_data

def convert_timestr_to_timestamp(in_str):
    real_timestamp = 0
    now_timestamp = datetime.datetime.now()
    if('小时前' in in_str):
        in_str = in_str.replace("小时前", "")
        real_timestamp = now_timestamp - datetime.timedelta(hours = int(in_str))
    elif('天前' in in_str):
        in_str = in_str.replace("天前", "")
        real_timestamp = now_timestamp - datetime.timedelta(days = int(in_str))
    elif('月前' in in_str):
        in_str = in_str.replace("个月前", "")
        real_timestamp = now_timestamp - datetime.timedelta(days = int(in_str)*30)
    elif('年前' in in_str):
        in_str = in_str.replace("年前", "")
        real_timestamp = now_timestamp - datetime.timedelta(years = int(in_str))
    elif('-' in in_str):
        #2018-01-01这种格式
        time.mktime(datetime.datetime.strptime(in_str, "%Y-%m-%d").timetuple())
    else:
        print (urllib.parse.quote(in_str)) #debug输出
        return None #返回None以防漏监控
    return real_timestamp
    
#fetch_url = 'http://m.sogou.com.inner/web/searchList.jsp?keyword=%E9%83%91%E7%88%BD%E5%85%AC%E5%BC%80%E7%A7%80%E6%81%A9%E7%88%B1'
res = asyncio.get_event_loop().run_until_complete(verify_news(wordlist))