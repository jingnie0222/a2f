from pyppeteer import launch
import asyncio,json
from urllib.parse import urlparse
import DataFile
import UserAgent
import time
import traceback
#pyppeteer的检查actions

#combo区，检查业务不相关但元素相关的操作，例如检查某个vrid是否存在等
async def combo_pc_get_vrid(page, vrid):
    vrid = str(vrid)
    result_divs = await page.querySelectorAll(".results>div")
    #print (len(result_divs))
    for i in range(1,len(result_divs)):
        seek_name = ".results>div:nth-of-type(" + str(i) + ") a[id*='" + str(vrid) + "']"
        check_exist = await action_is_element_exist(page, seek_name)
        if(check_exist):
            return ".results>div:nth-of-type(" + str(i) + ")"
    print ("".join(["vrid ", vrid, " not exits."]))
    return None
    
async def combo_wap_get_vrid(page, vrid):
    vrid = str(vrid)
    result_divs = await page.querySelectorAll(".results>div")
    #print (len(result_divs))
    for i in range(1,len(result_divs)):
        seek_name = ".results>div:nth-of-type(" + str(i) + ") a[id*='" + str(vrid) + "']"
        check_exist = await action_is_element_exist(page, seek_name)
        if(check_exist):
            return ".results>div:nth-of-type(" + str(i) + ")"
    print ("".join(["vrid ", vrid, " not exits."]))
    return None
    
#action区，这部分功能是和具体业务逻辑不相干的操作，例如检查某个元素是否存在。
async def action_get_page_content(page):
    content = await page.evaluate('document.documentElement.outerHTML', force_expr=True)
    return content
    
async def action_get_elements_content(page, div_selector_to_get):
    result_arr = []
    elements = await page.querySelectorAll(div_selector_to_get)
    for element in elements:
        el_content = await page.evaluate('(element) => element.textContent', element)
        result_arr.append(el_content)
    return result_arr

async def action_is_element_exist(page, check_el):
    el = await page.querySelector(check_el);
    if(el is None):
        return False
    else:
        return True

async def action_get_element_attr(page, selector, attr):
    element = await page.querySelector(selector)
    data = await page.evaluate('(element) => element.' + attr, element)
    return data
        
async def action_get_content(page, div_selector_to_get):
    element = await page.querySelector(div_selector_to_get)
    return await page.evaluate('(element) => element.textContent', element)

#删除所有的selector指向元素    
async def action_remove_all_element(page, div_selector_to_remove):
    await page.evaluate('''(sel) => {
        var elements = document.querySelectorAll(sel);
        for(var i=0; i< elements.length; i++){
            elements[i].parentNode.removeChild(elements[i]);
        }
    }''', div_selector_to_remove)
    return True
    
#load页面并返回结果
async def _action_combo_get_page_content(url, cookies_dir = 'data/cookies/'):
    try:
        #解析url属于那个domain
        parsed_uri = urlparse(url)
        cookies_file = "".join([cookies_dir, parsed_uri.netloc, "cookie"])
        my_cookie_file = DataFile.read_file_intostr(cookies_file)
        browser = await launch({"executablePath": "chromium-browser", "args": ["--no-sandbox"]})
        page = await browser.newPage()
        #读取cookies
        if(len(my_cookie_file) > 0):
            my_cookie_object = json.loads(my_cookie_file)
            print ("".join(["Load ", str(len(my_cookie_object)), " cookie item(s)."]))
            for row in my_cookie_object:
                await page.setCookie(row)        
        #设置UA
        ua_box = UserAgent.UserAgentBox()
        await page.setUserAgent(ua_box.wap_normal_user)
        await page.goto(url)
        new_cookie = await page.cookies()
        json_cookie = json.dumps(new_cookie)
        res = await action_get_page_content(page)
        DataFile.write_full_file(cookies_file, json_cookie)
        await browser.close()
        return res
    except Exception as e:
        traceback.print_exc()
        return ""

def action_combo_get_page_content(url, sleep_time = 1, cookies_dir = 'data/cookies/'):
    res = asyncio.get_event_loop().run_until_complete(_action_combo_get_page_content(url, cookies_dir))
    time.sleep(sleep_time)
    return res