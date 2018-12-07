import grequests,time,requests
import DBHelper
import Mail as mail
import Template
import DataFile
import PuppeteerActions as ppa
import UserAgent

fetch_filename = 'data/TOPURL_RANDOM' #抓取词表
general_timeout = 5 #第一次抓取的超时时间
retry_timeout = 6 #重试的超时时间

fetch_base = [] #存放需要抓取的url列表
vrid_base = [] #存放VRID
query_base = [] #存放query
name_base = [] #存放vr名称
bad_result_base = [] #存放bad result的仓库
bad_url_base = [] #存放失效url的仓库

proxies = {
  'http': 'http://10.142.10.140:3128',
  'https': 'http://10.142.10.140:3128',
}

http_status_comment = { '-1' : "连接" + str(retry_timeout) + "秒后超时", '403' : "禁止访问", '404' : "找不到页面", '5xx' : "对方服务器暂时不可用。500到511比较常见都是挂了。", "VRID为-1" : "原始数据里VRID为脏数据无法解析"}

#初始化一些标志容器
url_order = 0 #标志位，用来在循环里面取url列表第几个url，用于放置在里面
null_result = 0
bad_result = 0
whitelist_result = 0

#一些配置项
maillist = 'fanghuizhi@sogou-inc.com;fengmengmeng@sogou-inc.com;zhoupeng@sogou-inc.com;yuweidong@sogou-inc.com;'
#maillist = 'fanghuizhi@sogou-inc.com;'

#抓取白名单，实际上叫黑名单更好一点？
#因为是内部结果页/首页，不再进行抓取
fetch_whitelist_prototype = ['www.sogou.com', 'wap.sogou.com', 'm.sogou.com', 'wap.sogou.com', 'm.sogo.com', 'wap.sogo.com']
proxy_whitelist = ['m.haodf.com'] #当命中 proxy_whitelist 的时候使用proxy访问
temp_whitelist = ['m.haodf.com', 'm.douban.com', "movie.douban.com", "baike.m.sogou.com"] #因为对方站点屏蔽，临时不再抓取的白名单
for row in temp_whitelist:
    fetch_whitelist_prototype.append(row)

fetch_whitelist = []
for el in fetch_whitelist_prototype:
    fetch_whitelist.append("http://" + el)
    fetch_whitelist.append("https://" + el)
        
#初始化错误VRID的类型计数器
error_counter = Template.Counter('错误VRID统计')

#检查单行数据的data格式是否正常
def check_data_line(in_data):
    if(not len(in_data) == 4):
        return False
    if(len(in_data[3]) <= 0):
        return False
    if(not in_data[3][0:4] == "http"): #非http开头的说明是错误url
        return False
    url_v_tmp = in_data[3].split("://")
    if(len(url_v_tmp) < 2):
        return False
    return True
    
def check_in_whitelist(url_to_check, whitelist):
    for row in whitelist:
        if(row in url_to_check):
            return True
    return False
    
def try_parse_int(in_string):
    try:
        return int(in_string)
    except ValueError:
        return -1
    
with open(fetch_filename, 'r' , encoding="gbk") as fp: #注意原始文件是gbk的
    for line in fp:
        try:
            line = line.strip()
            data = line.split("\t")
            need_fetch = True #是否进行检查的mark

            check_line_good = check_data_line(data)
            if(not check_line_good):
                need_fetch = False
                null_result = null_result + 1
                bad_url_base.append( {"url" : data[3], "vrid" : data[1]})
            if(check_in_whitelist(data[3], fetch_whitelist)):
                whitelist_result = whitelist_result + 1
                need_fetch = False
            if(need_fetch):#修改了入库位置
                fetch_base.append(data[3])
                vrid_base.append(data[1].replace(",", '')) #把VRID包含的脏数据逗号干掉
                name_base.append("")
                query_base.append(data[0])
        except Exception as e:
            print ("Got an error line...")
            print (e)
            null_result = null_result + 1
            bad_url_base.append({"url" : line.strip(), "vrid": "N/A"})

print ("Load wordlist:" + str(len(fetch_base)) + ", with " + str(len(bad_url_base)) + " bad url in it, and " + str(whitelist_result) + " urls in whitelist, need not to verify.")
    
start_time = time.time()
print (start_time)

def async_fetch(urls, ua, referer, general_timeout = 10):
    i_headers = {'User-Agent': ua, 'referer': referer}
    results = grequests.map((grequests.get(u, timeout=general_timeout, headers = i_headers) for u in urls), size=20)
    return results
    
def htmlspecialchars(in_str):
    return in_str.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

ua_box = UserAgent.UserAgentBox()
real_spider_ua = ua_box.wap_spider

referer = 'https://m.sogou.com/web/searchList.jsp?uID=2zp0T_nmo6NADjuK&v=5&dp=1&w=1278&t=1533784250010&s_t=1533784260287&s_from=result_up&htprequery=%E4%B8%89%E6%98%9F%E6%B7%BB%E5%8A%A0%E5%89%82&keyword=marine+dreamin&pg=webSearchList&s=%E6%90%9C%E7%B4%A2&suguuid=8cf90615-8503-4978-ad26-f306ab607aac&sugsuv=AAEbUQkWIQAAAAqUJy6%2BHQsAkwA%3D&sugtime=1533784260292'
rs_group = async_fetch(fetch_base, real_spider_ua, referer, general_timeout)
print ("Fetch completed...")

allow_http_code = [200, 201, 202, 203, 204, 205, 206, 304]

for rs in rs_group:
    rs_retry = None #重试标签
    if rs is not None:
        if(not rs.status_code in allow_http_code):
            error_counter.add_counter(str(vrid_base[url_order]))
            bad_result = bad_result + 1
            bad_result_base.append({"status_code" : rs.status_code, "vrid" : vrid_base[url_order], "link" : fetch_base[url_order], "name" : name_base[url_order], "query" : query_base[url_order], "responser" : 'N/A'})
    else:
        #对超时的先进行进行一次重试
        try:
            rs_retry = requests.get(fetch_base[url_order], timeout=retry_timeout)
        except Exception as e:
            print (e)
        if(rs_retry is None): #如果重试还是跪就添加到失败列表里
            error_counter.add_counter(str(vrid_base[url_order]))
            bad_result_base.append({"status_code" : "-1", "vrid" : vrid_base[url_order], "link" : fetch_base[url_order], "name" : name_base[url_order], "query" : query_base[url_order], "responser" : 'N/A'})
            bad_result = bad_result + 1
        elif(not rs_retry.status_code in allow_http_code):
            error_counter.add_counter(str(vrid_base[url_order]))
            bad_result_base.append({"status_code" : rs_retry.status_code, "vrid" : vrid_base[url_order], "link" : fetch_base[url_order], "name" : name_base[url_order], "query" : query_base[url_order], "responser" : 'N/A'})
            bad_result = bad_result + 1
    url_order = url_order + 1
    
end_time = time.time()
cost = end_time - start_time


#开始写输出报告
output_filename = 'data/vr_deadlink_tmpout.html' #临时报告文件输出地
wfp = open(output_filename, 'w+', encoding="utf-8")
wfp.write('<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/></head><body>') #html的头部

summary_str = '' #summary_str 是整个报告里的总结片段
summary_str = summary_str + Template.html_general_css() + '<span class="tip">VR死链专项监控</span><table class="bx"><thead><tr><td>监控链接数</td><td>异常连接数</td><td>死链率</td><td>无效源数据量</td></tr></thead>'
repo_str = "</td><td>".join([str(url_order), str(bad_result), str((bad_result / url_order) * 100 )[0:4] + '%', str(null_result)])
summary_str = summary_str + '<tbody><tr><td>' + repo_str + '</td></tr></tbody></table>'
wfp.write(summary_str)
comment_str_data = ["<p>状态码参考："]
for k,v in http_status_comment.items():
    comment_str_data.append(k + " : " + v + " |")
comment_str_data.append("</p>")
wfp.write("".join(comment_str_data))
    
#按VRID 做group 统计有问题的VR数量，并初始化负责人dict
error_count_dict = error_counter.get_counter_dict()
error_responser_dict = {}

#统计异常连接
problem_str = '<span class="tip">异常链接</span>' #problem_str 是整个报告里的问题详情片段
problem_str = problem_str + '<table class="bx"><thead><tr><td>VR名称</td><td>VRID</td><td>负责人</td><td>QUERY</td><td>链接</td><td>状态码</td></tr></thead>'
problem_box = []
vrdb = DBHelper.init_db('conf/mysql.conf', 'vrresource')
for tline in bad_result_base:
    vr_info = vrdb.fetch_first("SELECT * FROM vr_resource WHERE vr_id=" + str(tline['vrid']))
    if(vr_info is None):
        #获取为空，尝试get vrid末尾2位为0的数据
        vr_info = vrdb.fetch_first("SELECT * FROM vr_resource WHERE vr_id=" + str(tline['vrid'])[0:6] + "00")
        if(vr_info is None): #如果还获取不到只能填N/A了
            pass
        else:
            tline['name'] = vr_info['res_name']
            tline['responser'] = vr_info['principal']
            #对tline的数据类型进行检查，这个mysql lib太弱智了
            if(tline['name'] is None):
                tline['name'] = 'N/A'
            if(tline['responser'] is None):
                tline['responser'] = 'N/A'
    else:
        tline['name'] = vr_info['res_name']
        tline['responser'] = vr_info['principal']
        if(tline['name'] is None):
            tline['name'] = 'N/A'
        if(tline['responser'] is None):
            tline['responser'] = 'N/A'
    final_responser = str(tline.get('responser', "N/A"))
    final_vrid = try_parse_int(tline.get('vrid', -1))
    if(final_vrid > 0):
        error_responser_dict[final_vrid] = final_responser
    in_rr = "</td><td>".join([tline.get('name', "N/A"), str(final_vrid), final_responser , htmlspecialchars(tline.get('query', "")), htmlspecialchars(tline.get('link', "")), str(tline.get('status_code', -1))])
    problem_box.append('<tr><td>' + in_rr + '</td></tr>' + "\n")
problem_str = problem_str + "".join(problem_box)
problem_str = problem_str + '</table>'

#把VRID 做group 统计有问题的VR数量这部分统计输出
error_count_data = []
for k,v in error_count_dict.items():
    error_count_data.append([str(k), str(v), error_responser_dict.get(k, "N/A")])
#依靠value对error_count_data进行排序
error_count_data.sort(key=lambda x:try_parse_int(x[1]), reverse=True)
wfp.write(Template.html_table(error_count_data, ["VRID", "次数", "负责人"]))
wfp.write(problem_str) #将片段写入到文件里面
wfp.write('<div>本次运行白名单：' + ",".join(fetch_whitelist) + ', 完全匹配共忽略 ' + str(whitelist_result) + ' 个数据。</div>')
#记录脏数据
wfp.write('<table><thead><tr><td>因脏数据完全错误过滤的URL</td><td>VRID</td></tr></thead><tbody>')
for tline in bad_url_base:
    wfp.write('<tr><td>' + tline.get("url", "N/A") + '</td><td>' + str(tline.get("vrid", "N/A")) + '</td></tr>' + "\n")
wfp.write('</tbody></table>')
wfp.write('<div>本次运行耗时：' + str(cost) + ' 秒. UA:' + real_spider_ua + ' </div>')
wfp.write('<div>本次运行时间：' + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '</div>')
wfp.write('</body></html>')
wfp.close()

#只有发现问题的情况下才发送报警邮件，bad_result计数大于0
if(bad_result > 0):
    print ("Need send mail...")
    mail.sendMail("VR死链专项监控", output_filename, maillist)
else:
    print ("All result seems good.")

mydb = DBHelper.init_db('conf/mysql.conf', 'test_base')
mydb.insert('vr_fetch_history_log', {"check_link" : url_order, "error_link" : bad_result, "error_rate" : str((bad_result / url_order) * 100 )[0:4] + '%', "summary": summary_str, "problem" : problem_str})

print (cost)
print ("Task done")

