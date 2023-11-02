import os
import re
import time

from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from selenium.webdriver.common.by import By

# 存放搜索的关键字
global search

# 判断是否为中文摘要


def Chinese(web):
    try:
        web.find_element(By.XPATH, '//*[@id="ChDivSummary"]')
        return True
    except:
        return False

# 判断是否存在下一页


def Next_page(web):
    try:
        web.find_element(By.XPATH, '//*[@id="PageNext"]')
        return True
    except:
        return False

# 判断是否为英文摘要


def English(web):
    try:
        web.find_element(By.XPATH, '//*[@id="doc-summary-content-text"]')
        return True
    except:
        return False

# 判断是否打开了子网页


def is_childpage(web):
    try:
        web.switch_to.window(web.window_handles[1])
        return True
    except:
        return False

# 爬取数据


def spider(web):
    # key_search = input('请输入索引关键字：')
    # 获取所有成分，存放到medical_list中
    medical_list = get_data()
    print(medical_list)
    # 已抓取过的文章存放到列表have_search_list = []
    have_search_list = []
    # 用一个变量来标明第一次搜索和后面几次搜索
    count_mark = 0
    for key_search in medical_list:
        # 给全局变量赋值
        global search
        search = key_search
        # 如果已经抓取过，则跳过，进行下一个
        if key_search in have_search_list:
            continue
        else:
            have_search_list.append(key_search)
            # 每个成分创建一个文件夹
            file_path = './Abstract/'+key_search
            if not os.path.exists(file_path):
                os.mkdir(file_path)

        if count_mark == 0:
            web.find_element(
                By.XPATH, '//*[@id="txt_SearchText"]').send_keys(key_search, Keys.ENTER)
            count_mark += 1
        else:
            web.find_element(By.XPATH, '//*[@id="txt_search"]').clear()
            web.find_element(
                By.XPATH, '//*[@id="txt_search"]').send_keys(key_search, Keys.ENTER)
        # input('筛选是否完成：')
        # 筛选年份
        # time.sleep(4)
        time.sleep(4)
        # while循环实现翻页
        page_count = 0
        while True:
            try:
                time.sleep(2)
                # 获取论文列表
                page_count += 1
                tr_list = web.find_elements(
                    By.XPATH, """//*[@id="gridTable"]/table/tbody/tr""")
                print(f'{key_search} : 正在读取第{page_count}页!')
                # //*[@id="gridTable"]/table/tbody/tr[1]/td[3]
                for tr in tqdm(tr_list):
                    # time.sleep(1)
                    try:
                        user = tr.find_element(By.XPATH, './td[3]').text
                        journal = tr.find_element(By.XPATH, './td[4]/a').text
                        publish = tr.find_element(By.XPATH, './td[5]').text
                    except:
                        user = ""
                        journal = ""
                        publish = ""
                    # 点击论文链接
                    tr.find_element(By.XPATH, './td/a[@class="fz14"]').click()
                    # 切换到新窗口
                    if is_childpage(web) == True:
                        web.switch_to.window(web.window_handles[1])
                    else:
                        print('*'*100)
                        print('未打开新窗口')
                        time.sleep(50)
                        continue
                    # time.sleep(3)
                    # 中文期刊
                    if Chinese(web) == True:
                        # 抓取标题
                        title = web.find_element(
                            By.XPATH, '/html/body/div[@class="wrapper"]/div[@class="main"]/div[@class="container"]/div[@class="doc"]/div[@class="doc-top"]/div[@class="brief"]/div[@class="wx-tit"]/h1').text
                        # 抓取摘要
                        abstract = web.find_element(
                            By.XPATH, '//*[@id="ChDivSummary"]').text
                    # 英文期刊
                    elif English(web) == True:
                        # 抓取标题
                        title = web.find_element(
                            By.XPATH, '//*[@id="doc-title"]').text
                        # 抓取摘要
                        abstract = web.find_element(
                            By.XPATH, '//*[@id="doc-summary-content-text"]').text
                    else:
                        title = "标题不存在！"
                        abstract = ''

                    # 如果标题中存在/则用汉字替换
                    r = r"[.!+-=——,$%^，,。？?、~@#￥%……&*《》<>「」{}【】()/\\\[\]'\"]"
                    title_copy = re.sub(r, ' ', title)
                    # title_copy = re.sub(r'/','斜杠',title)

                    # print(title)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    # print(abstract)

                    # 写入摘要
                    try:
                        with open(file_path + '/result.txt', 'a', encoding='utf-8') as f:
                            f.write(user)
                            f.write('@')
                            f.write(journal)
                            f.write('@')
                            f.write(publish)
                            f.write('@')
                            f.write(title)
                            f.write('@')
                            f.write(abstract)
                            f.write('\n')
                        if is_childpage(web) == True:
                            # 关闭子网页
                            web.close()
                            # 切换到原网页
                            web.switch_to.window(web.window_handles[0])
                        else:
                            web.switch_to.window(web.window_handles[0])
                    except:
                        print('文件名称Invalid !')
                        if is_childpage(web) == True:
                            # 关闭子网页
                            web.close()
                            # 切换到原网页
                            web.switch_to.window(web.window_handles[0])
                        else:
                            web.switch_to.window(web.window_handles[0])
                if Next_page(web) == True:
                    # web.find_element('//*[@id="PageNext"]').click()
                    web.find_element(
                        By.XPATH, '/html/body').send_keys(Keys.RIGHT)
                else:
                    break
                # time.sleep(3)
            except:
                print('定位失败！当前在第{}页！'.format(page_count))
                # 跳回第一个页面
                if is_childpage(web) == True:
                    web.switch_to.window(web.window_handles[1])
                    web.close()
                    web.switch_to.window(web.window_handles[0])
                else:
                    web.switch_to.window(web.window_handles[0])
                # 点击下一页
                if Next_page(web) == True:
                    # web.find_element('//*[@id="PageNext"]').click()
                    web.find_element(
                        By.XPATH, '/html/body').send_keys(Keys.RIGHT)
                    time.sleep(5)
                else:
                    break
        print('药物：', key_search, 'Successful!')

# 筛选中文、年份


def Choose_year(web):
    count = 0
    while True:
        try:
            time.sleep(10)
            # 点击中文
            web.find_element(
                By.XPATH, '/html/body/div[3]/div[1]/div/div/div/a[1]').click()
            time.sleep(8)
            web.find_element(
                By.XPATH, '//*[@id="divGroup"]/dl[3]/dt/i[1]').click()
            time.sleep(8)
            web.find_element(
                By.XPATH, '//*[@id="divGroup"]/dl[3]/dt/i[2]').click()
            time.sleep(8)
            web.find_element(
                By.XPATH, '//*[@id="txtStartYear"]').send_keys(2015)
            time.sleep(3)
            web.find_element(By.XPATH, '//*[@id="txtEndYear"]').send_keys(2021)
            time.sleep(3)
            web.find_element(By.XPATH, '//*[@id="btnFilterYear"]').click()
            break
        except:
            web.refresh()
            # 重新输入
            web.find_element(By.XPATH, '//*[@id="txt_search"]').clear()
            time.sleep(2)
            web.find_element(
                By.XPATH, '//*[@id="txt_search"]').send_keys(search, Keys.ENTER)
            count += 1
            if count > 15:
                time.sleep(120)
            if count > 21:
                break


# 从本地csv文件中读取成分
def get_data():
    medical = ['洪涝', '洪水', '洪涝灾害']
    # medical.append(input("请输入")) '灾害','自然灾害','滑坡',
    print('文章读取完成！')
    return medical


if __name__ == '__main__':
    if not os.path.exists('./Abstract'):
        os.mkdir('./Abstract')

    # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # # 设置不显示窗口
    # options.add_argument('--headless')
    # # 创建一个谷歌驱动器
    # driver = webdriver.Chrome(options=options)

    opt = Options()
    opt.add_experimental_option('excludeSwitches', ['enable-automation'])
    opt.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2})
    #
    opt.add_argument('--headless')
    opt.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36')
    url = 'https://www.cnki.net/?pageId=77825&wfwfid=145305&websiteId=58201'
    web = Chrome(options=opt)
    web.get(url)
    # while True:
    spider(web)
    # choice = input('是否搜索下一个关键字（是/否）：')
    # if choice == '否':
    #     break
