#通用抓取和验证工具
#fanghuizhi@sogou-inc.com
#使用pyppeteer做复杂验证

import asyncio,urllib,os,time,requests
from pyppeteer import launch
import DBHelper
import Mail as mail
import Template
import DataFile
import PuppeteerActions as ppa

async def main():
    report_html_path = 'report/special_temp_wap.html'
    report_title = "官网展现检查专项监控"
    report_title_h3 = "WAP检查结果"
    report_headinfo = ["预期URL", "QUERY", "现场HTML", "现场截图", "原因"]
    report_time = Template.html_timestamp_dirable(time.time())
    report_html_front = "".join(['http://rsync.frontqa39.web.sjs.ted/vrfetch/' , report_time , "/"]) #报告现场html和截图访问的地址前缀
    report_html_local_dir = "".join(['report/', report_time, '/'])
    maillist = "fanghuizhi@sogou-inc.com;"
    print_interval = 20 #工具运行抓取20个就提示一下
    offical_file_path_wap = "data/offical_file_wap"
    fetch_url_front = 'http://wap.sogou.com.inner/web/searchList.jsp?keyword='
    click_view_tip = "点击查看"
    reason_not_is_offical = "第一条没有打官网标签"
    reason_not_is_url_equal = "第一条url和预期的不符"
    source_content = "http://umis.sogou-inc.com/ubs?act=outputRecord&table=ubs_white_web_officialSite_url 随机抽取 + 固定词表"
    good_source_path = "data/tmp/m_wap_gg.txt" #放置好结果的位置

    fetch_url_bases_wap = DataFile.load_data_file(offical_file_path_wap, ["query", "url"]) #加载数据

    browser = await launch({"executablePath": "chromium-browser", "args": ["--no-sandbox"]})
    page = await browser.newPage()
    
    good_result_list = []
    
    #抓取WAP结果
    report_list = Template.ReportData(report_title_h3, report_headinfo, print_interval=print_interval, print_excepted_count=len(fetch_url_bases_wap))
    for fetch_url_base in fetch_url_bases_wap:
        #根据query加工获得encode的query和抓取url
        query_urlencoded = urllib.parse.quote(fetch_url_base["query"])
        fetch_url = "".join([fetch_url_front, query_urlencoded])
        await page.goto(fetch_url)
        await mod_wap_remove_ad(page) #移除广告
        is_offical = await check_wap_if_first_offical(page)
        is_url_equal = await check_wap_if_first_link_good(page, fetch_url_base["url"])
        if(not is_offical or (not is_url_equal)):
            my_rs = await make_record(page, "wap_" + query_urlencoded, report_html_local_dir, report_html_front)
            my_rs.set_checkpoint([{"is_pass" : is_offical, "reason_content" : reason_not_is_offical}, {"is_pass" : is_url_equal, "reason_content" : reason_not_is_url_equal}])
            report_list.add_data([fetch_url_base["url"], Template.html_a_link(fetch_url ,fetch_url_base["query"]), Template.html_a_link(my_rs.get_remote_html_path(), click_view_tip), Template.html_a_link(my_rs.get_remote_png_path(), click_view_tip), my_rs.get_checkpoints_reason()])
        else:
            good_result_list.append(fetch_url_base["query"] + "\t" + fetch_url_base["url"])
        report_list.add_fetch_count() #添加抓取计数器
    report_list.set_end_time()
    
    print ("WAP fetch ends...")
    await browser.close()
    
    #DataFile.write_full_file("data/tmp/m_wap_gg.txt", "\n".join(good_result_list))
    #输出报告
    with open(report_html_path, 'w+', encoding='utf-8') as wfp:
        wfp.write(Template.html_general_css())
        wfp.write(report_list.get_table_summary())
        wfp.write(Template.html_p_data_source(source_content))
    report_content = mail.sendMail(report_title, report_html_path, maillist, use_nl2br = False)
    
    #往DB里写入报告
    db = DBHelper.init_db("conf/mysql.conf", "test_base")
    db.insert("special_check_result", {"type" : "offical_tag_wap", "report_content" : report_list.get_table_summary(), "word_count" : report_list.get_fetch_count(), "error_count" : report_list.get_error_count()})
    
    
#检查是否为官网，这个数据是基于前端的    
async def check_wap_if_first_offical(page):
    check_offical_namestr = ".results>div:nth-of-type(1) span[class*='web-tag']" #result下子元素的第一个div(nth-of-type)。然后选择包含web-tag的 css selector的包含是 *=
    check_offical_content_expected = "官网"
    return await check_if_first_offical(page, check_offical_namestr, check_offical_content_expected)
        
async def check_if_first_offical(page, check_offical_namestr, check_offical_content_expected):    
    exist_info = await ppa.action_is_element_exist(page, check_offical_namestr)
    if(exist_info):
        con = await ppa.action_get_content(page, check_offical_namestr)
        if(con == check_offical_content_expected):
            return True
        else:
            print (con)
            return False
    else:
        return False
      
async def check_wap_if_first_link_good(page, ck_url):
    get_url = await ppa.action_get_element_attr(page, ".results>div:nth-of-type(1) a:nth-of-type(1)", "href")
    #解析wap前端拿回来的点出url，这个需要把&url给砍出来
    real_url = get_url.split("url=")[1].split("&")[0]
    real_url = urllib.parse.unquote(real_url)
    if(ck_url in real_url):
        return True
    elif(ck_url in real_url.replace("http://", "https://")):
        return True
    print (real_url + ",check:" + ck_url)
    return False
      
#发现问题后记录content
async def make_record(page, record_name, report_html_local_dir, report_html_front):
    my_rs_tmp = Template.ReportScene(record_name, report_html_local_dir, report_html_front)
    await page.screenshot({'path': my_rs_tmp.get_local_png_path(), 'fullPage': True}) 
    full_html = await ppa.action_get_page_content(page)
    DataFile.write_full_file(my_rs_tmp.get_local_html_path(), full_html)
    return my_rs_tmp
        
#删除广告div
async def mod_wap_remove_ad(page):
    await ppa.action_remove_all_element(page, '.ec_ad_results')
    return True

asyncio.get_event_loop().run_until_complete(main())
print ("All task done.")