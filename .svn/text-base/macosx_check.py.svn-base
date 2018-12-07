#自动检查macosx的更新
#数据来源是官网  https://support.apple.com/zh_CN/downloads

import requests,time
import DBHelper
import Mail as mail
import json
import Template
import DataFile

#各种配置项
mydb = DBHelper.init_db('conf/mysql.conf', 'test_base')
mail_title = "MAC OS X 专项监控"
detector_mail = 'fanghuizhi@sogou-inc.com;' #debug开发者接收邮件，当抛异常的时候及时通知修改
info_maillist = 'fanghuizhi@sogou-inc.com;zhanghaoli@sogou-inc.com;chenchen@sogou-inc.com;jianglin@sogou-inc.com;sonicfeng@sogou-inc.com;' #订阅者接收邮件
#info_maillist = 'fanghuizhi@sogou-inc.com;'
output_file_tmp = 'tmp_mac_os_x_detector.html'
error_file_tmp = 'tmp_mac_os_x_error.html'
need_sendmail = False
main_table_name = "mac_osx_update_check_log"

def get_fetch_page(page):
    return 'https://km.support.apple.com/kb/index?page=downloads_browse&offset=' + str(page) + '&sort=recency&facet=all&loadmore=true&category=PF6&locale=zh_CN&callback=ACDownloadSearch.showResults'    
    
try:
    print ("Task start in " + Template.html_timestamp_dirable(time.time()))
    wfp = open(output_file_tmp, 'w+', encoding="utf-8")

    rs = requests.get(get_fetch_page(0), headers={"User-Agent": 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko', "Referer" : "https://support.apple.com/zh_CN/downloads/macos", "Host":"km.support.apple.com"})
    in_ar = rs.text
    data_tmp_1 = in_ar.split("ACDownloadSearch.showResults(")
    data_fr = data_tmp_1[1]
    data_fr = data_fr[:-2]
    json_data = json.loads(data_fr)
    for download_item in json_data['downloads']:
        #检查这条是否已经入库
        sql = "".join(["SELECT * FROM ", main_table_name, " WHERE inner_id='", download_item['id'], "'"])
        print ("".join(["check sql:" , sql]))
        query_rs = mydb.query(sql)
        if(query_rs is None or (len(query_rs) <= 0)):
            mydb.insert(main_table_name, {"inner_id" : download_item['id'], "download_url": download_item['fileurl'], "desc": download_item['description'], "add_timestamp" : time.time(), "lastmodified" : download_item['lastmodified'], "url" : "https://km.support.apple.com/" + download_item['url']})
            wfp.write("".join(["检测到一条新的mac更新, 更新内容为 ", download_item['description'], "\n<br />下载地址" , "https://km.support.apple.com/" , download_item['url'], "\n<br />"]))
            wfp.write(Template.html_general_css())
            #获取checklist和vrlist
            check_vr = mydb.query("SELECT * FROM mac_osx_update_check_vr", bycolumnname = True)
            table_head_1 = ["VRID", "VR名称", "Query"]
            table_data_1 = []
            for row in check_vr:
                table_data_1.append([str(row['vrid']), row['vrname'].decode(), row['query'].decode()])
            wfp.write(Template.html_h3_title("VR相关 query 列表"))
            wfp.write(Template.html_table(table_data_1, table_head_1))
            
            check_list = mydb.query("SELECT * FROM mac_osx_update_check_list", bycolumnname = True)
            table_head_2 = ["位置", "QUERY", "检查点"]
            table_data_2 = []
            for row in check_list:
                table_data_2.append([row['pos'].decode(), row['query'].decode(), row['check'].decode()])
            wfp.write(Template.html_h3_title("Checklist"))
            wfp.write(Template.html_table(table_data_2, table_head_2))
            need_sendmail = True
    if(len(download_item) <= 0):
        wfp.write ("警报，没有侦测到合适的数据，苹果官网可能已经修改，及时检查…")
        wfp.close()
        mail.sendMail(mail_title, output_file_tmp , detector_mail)
    else:
        wfp.close()
        if(need_sendmail):
            mail.sendMail(mail_title, output_file_tmp , info_maillist) #如果侦测到有新的更新，则向订阅者发送
        else:
            print ("All result already in db. need not to send mail.")
    
        
except Exception as e:
    print ("Got some error...")
    print (e)
    wfp_err = open(error_file_tmp, 'w+', encoding="utf-8")
    wfp_err.write("".join(["警报，检测器出现异常，具体内容是:\n", str(e), "\n"]))
    wfp_err.close()
    mail.sendMail(mail_title, error_file_tmp , detector_mail)