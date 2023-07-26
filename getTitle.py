# -*- coding:utf-8 -*-
import re
import requests
import urllib3
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xlwt
import xlrd
from xlutils.copy import copy
from randomUA import user_agent
from tqdm import tqdm
from printLogo import printlogo

logging.captureWarnings(True)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

start = time.time()
lock = threading.Lock()
savefilename = time.strftime("%Y-%m-%d %H.%M.%S")


def write_xls_title():
    myxls = xlwt.Workbook()
    sheet1 = myxls.add_sheet(u'title', cell_overwrite_ok=True)
    sheet1.write(0, 0, "源地址")
    sheet1.write(0, 1, "跳转地址")
    sheet1.write(0, 2, "状态码")
    sheet1.write(0, 3, "标题")
    myxls.save(savefilename + '.xls')


def solve_url():
    # url.txt中ip:port格式转换成http、https格式，保存到url-run.txt中
    with open("url.txt", "r") as f:
        line = f.readlines()

    with open("url-run.txt", "w") as f2:
        for i in line:
            i = i.strip('\n')
            if 'http://' not in i and 'https://' not in i:
                f2.write('http://' + i + '\n')
                f2.write('https://' + i + '\n')
            else:
                f2.write(i + '\n')


# 获取状态码、标题





def get_codetitle(url):
    code = "无法访问"
    title = " "
    resurl = " "
    try:
        urllib3.disable_warnings()
        header = {
            'User-Agent': user_agent(),
        }
        res = requests.get(url, headers=header, verify=False, allow_redirects=True, timeout=(3, 9))
        res.encoding = res.apparent_encoding
        code = res.status_code
        title = re.findall("(?<=\<title\>)(?:.|\n)+?(?=\<)", res.text, re.IGNORECASE)[0].strip()
        resurl = res.url
    except Exception as error:
        pass
    return resurl, code, title


def write(url,phar):
    codetitle = get_codetitle(url)
    resurl = str(codetitle[0])
    code = str(codetitle[1])
    title = str(codetitle[2])
    # print(url + "|" + resurl + "|" + code + "|" + title)
    phar.update(1)
    with lock:
        word_book = xlrd.open_workbook(savefilename + '.xls')
        sheets = word_book.sheet_names()
        work_sheet = word_book.sheet_by_name(sheets[0])
        old_rows = work_sheet.nrows
        heads = work_sheet.row_values(0)
        new_work_book = copy(word_book)
        new_sheet = new_work_book.get_sheet(0)
        i = old_rows
        new_sheet.write(i, 0, url)
        new_sheet.write(i, 1, resurl)
        new_sheet.write(i, 2, code)
        new_sheet.write(i, 3, title)
        new_work_book.save(savefilename + '.xls')


def main():
    printlogo();
    print("正在处理url。。。。。。。。")
    try:
        solve_url()
    except Exception as error:
        print("处理失败，请先在将链接放入根目录的url.txt中")
        return 0
    write_xls_title()
    # 获取url列表
    with open('url-run.txt', 'r', encoding='utf-8') as f:
        urls_data = [data.strip().strip('\\') for data in f]
        # 多线程
    with tqdm(total=len(urls_data)) as pbar:
        with ThreadPoolExecutor(max_workers=100) as ex:
            futures = [ex.submit(write, url, pbar) for url in urls_data]
    end = time.time()
    print("已生成完毕，总耗时:", end - start, "秒")


if __name__ == '__main__':
    main()
