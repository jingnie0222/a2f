#fanghuizhi@sogou-inc.com
#HTML生成类python
import time,datetime,hashlib,os

#问题计数器
class Counter:
    error_dict = {}
    def __init__(self, name):
        self.name = name
        
    def get_counter_dict(self):
        return self.error_dict
        
    def add_counter(self, i_key):
        if not i_key in self.error_dict:
            self.error_dict[i_key] = 1
        else:
            self.error_dict[i_key] = self.error_dict[i_key] + 1
            
    def sub_counter(self, i_key):
        if i_key in self.error_dict:
            self.error_dict[i_key] = self.error_dict[i_key] - 1
            
    def output_default_html(self, table_head):
        tmp_data = []
        for k,v in self.error_dict.items():
            tmp_data.append([k,v])
        return html_table(self.tmp_data, table_head)

#故障现场，输入名称、报告路径、Html访问前端路径，自动拼接
class ReportScene:
    checkpoints = []

    def __init__(self, name, local_report_dir, remote_report_dir):
        self.local_report_dir = local_report_dir
        self.remote_report_dir = remote_report_dir
        self.md5_name = hashlib.md5(name.encode("utf-8")).hexdigest()
        if not os.path.exists(local_report_dir):
            os.makedirs(local_report_dir)
        
    def get_local_png_path(self):
        return "".join([self.local_report_dir, self.md5_name, ".png"])
        
    def get_local_html_path(self):
        return "".join([self.local_report_dir, self.md5_name, ".html"])
        
    def get_remote_png_path(self):
        return "".join([self.remote_report_dir, self.md5_name, ".png"])
        
    def get_remote_html_path(self):
        return "".join([self.remote_report_dir, self.md5_name, ".html"])
        
    #添加检查点，如果为True则产生reason summary的时候不返回，如果False则会返回reason。
    def add_checkpoint(self, assert_var, reason_content):
        self.checkpoints.append({"is_pass" : assert_var, "reason_content" : reason_content})
        
    def set_checkpoint(self, in_checkpoints):
        self.checkpoints = in_checkpoints
        
    def get_checkpoints_reason(self):
        return_data = []
        for row in self.checkpoints:
            if(not row["is_pass"]):
                return_data.append(row["reason_content"])
        #print ("got "+ str(len(return_data)) + " checkpoints...")
        return ",".join(return_data)
        
#报告类
class ReportData:
    fetch_count = 0 #总共抓取了多少数据，因为报告里只记录了错误数据，因此需要有这一个计数器
    error_data = []
    print_interval = 0 #当大于0的时候，当add_data的时候，每间隔 print_interval 个数据就print一次报告
    print_message = ''
    print_excepted_count = 0 #预期抓取的数据总量
    start_time = 0
    end_time = 0
    
    #一些报告现场相关url的变量，用于保存文件，并在最终生成报告邮件里给用户点出

    #name为报告名称， report_headinfo为报告数据的表头list
    def __init__(self, name, report_headinfo, print_interval = 0, print_excepted_count = 0):
        self.name = name
        self.report_headinfo = report_headinfo
        self.print_interval = print_interval
        self.print_excepted_count = print_excepted_count
        self.set_start_time()
        print ("Report init.print_excepted_count:" + str(print_excepted_count) + ",print_interval:"+ str(print_interval))
        
    def add_fetch_count(self):
        self.fetch_count = self.fetch_count + 1
        if(self.print_interval > 0 and self.fetch_count % self.print_interval == 0):
            print ("".join(["[F2A Autotest]", self.print_message, "Process :" , str(self.fetch_count), '/', str(self.print_excepted_count)]))
        
    def set_start_time(self):
        self.start_time = time.time()
        
    def set_end_time(self):
        self.end_time = time.time()
        
    #重新设置报告间隔
    def set_process_setting(self, print_interval, print_excepted_count):
        self.print_interval = print_interval
        self.print_excepted_count = print_excepted_count
        
    def set_process_message(self, in_message):
        self.print_message = in_message
        
    def add_data(self, data_row):
        self.error_data.append(data_row)
        
    def get_table_summary(self): #获取当前数据的表格形式统计报告HTML
        return "".join([html_h3_title(self.name), html_p_error_rate(len(self.error_data), self.fetch_count), html_p_time(self.start_time, self.end_time), html_table(self.error_data, self.report_headinfo)])
        
    def get_fetch_count(self):
        return self.fetch_count
        
    def get_error_count(self):
        return len(self.error_data)

def html_general_css():
    return '<style>.bx{border: 1px solid #cbcbcb;empty-cells: show;border-collapse: collapse;border-spacing: 0;width: 95%} .bx thead{background-color: #5F9EA0;color: #FFFFFF ;text-align: left;vertical-align: bottom;} .bx td{border:#CCC solid 1px;} .tip {font-weight:700}</style>'

def html_h3_title(content):
    return "".join(["<h3>", content, "</h3>"])
    
#用来报告里添加注释，标示原始抓取数据来源
def html_p_data_source(content):
    return "".join(["<p>原始抓取数据来源：", content, "</p>"])
    
#把时间戳转化为目录名称
def html_timestamp_dirable(in_timestamp):
    return datetime.datetime.fromtimestamp(in_timestamp).strftime('%Y-%m-%d-%H-%M-%S')
    
#把时间戳转化为可读的形式
def html_timestamp_readable(in_timestamp):
    return datetime.datetime.fromtimestamp(in_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
#生成起始时间和最终输出
def html_p_time(start_time, end_time):
    return "".join(["<p>开始时间：<span>", html_timestamp_readable(start_time), "</span> 结束时间：<span>", html_timestamp_readable(end_time), "</span></p>", "<p>耗时：", str(end_time - start_time), "（秒）</p>"])
    
#生成错误比例的文字
def html_p_error_rate(bad_result, url_order):
    if(url_order == 0):
        return '-0.00%'
    return "".join([ '<p>抓取发现错误率：', str(bad_result), '/',str(url_order), '(', str((bad_result / url_order) * 100 )[0:4], '%)', '</p>'])
    
#生成html的table格式
def html_table(data, table_head = [], table_class="bx"):
    return_data = ["".join(['<table class="' , table_class , '">'])]
    return_data.append("<thead><tr>")
    if(len(table_head) > 0):
        return_data.append('<td>')
        return_data.append("</td><td>".join(table_head))
        return_data.append('</td>')
    return_data.append("</tr></thead>\n<tbody>")
    if(len(data) > 0):
        for row in data:
            return_data.append('<tr><td>')
            return_data.append("</td><td>".join(row))
            return_data.append("</td></tr>\n")
    return_data.append("</tbody></table>")
    return "".join(return_data)
    
def html_a_link(link, content):
    return "".join(['<a href="', link, '" target="_blank">', content, '</a>'])