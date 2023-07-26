import argparse
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import re
import urllib.parse
import time
import random

from CustomQueue import CustomQueue
from randomUA import user_agent

queueInt = CustomQueue()  # 存储内链的队列
queueExt = CustomQueue()  # 存储外链的队列

externalLinks = []
internalLinks = []


# 获取页面中所有外链的列表
def getExterLinks(bs, exterurl):
    # 找出所有以www或http开头且不包含当前URL的链接
    for link in bs.find_all('a', href=re.compile
        ('^(http|www)((?!' + urlparse(exterurl).netloc + ').)*$')):
        # 按照标准，URL只允许一部分ASCII字符，其他字符（如汉字）是不符合标准的，
        # 我们的链接网址可能存在汉字的情况，此时就要进行编码。
        link.attrs['href'] = urllib.parse.quote(link.attrs['href'], safe='?=&:/')
        if link.attrs['href'] is not None:
            #if link.attrs['href'] not in externalLinks:
            if link.attrs['href'] not in externalLinks:
                queueExt.enqueue(link.attrs['href'])
                externalLinks.append(link.attrs['href'])
                print(link.attrs['href'])


#     return externalLinks

# 获取页面中所以内链的列表
def getInterLinks(bs, interurl):
    interurl = '{}://{}'.format(urlparse(interurl).scheme,
                                urlparse(interurl).netloc)

    # 找出所有以“/”开头的内部链接
    for link in bs.find_all('a', href=re.compile
        ('^(/|.*' + urlparse(interurl).netloc + ')')):
        link.attrs['href'] = urllib.parse.quote(link.attrs['href'], safe='?=&:/')
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in internalLinks:
                # startsWith()方法用来判断当前字符串是否是以另外一个给定的子字符串“开头”的
                if (link.attrs['href'].startswith('//')):
                    if interurl + link.attrs['href'] not in internalLinks:
                        queueInt.enqueue(interurl + link.attrs['href'])
                        internalLinks.append(interurl + link.attrs['href'])
                elif (link.attrs['href'].startswith('/')):
                    if interurl + link.attrs['href'] not in internalLinks:
                        queueInt.enqueue(interurl + link.attrs['href'])
                        internalLinks.append(interurl + link.attrs['href'])
                else:
                    queueInt.enqueue(link.attrs['href'])
                    internalLinks.append(link.attrs['href'])


#     return internalLinks

def deepLinks():
    num = queueInt.size()
    while num > 1:
        i = queueInt.dequeue()
        if i is None:
            break
        else:
            print('访问的内链')
            print(i)
            print('找到的新外链')
            header = {
                'User-Agent': user_agent(),
            }
            #         html = urlopen(i)
            html = requests.get(i, headers=header)
            time.sleep(random.random() * 3)
            domain1 = '{}://{}'.format(urlparse(i).scheme, urlparse(i).netloc)
            bs = BeautifulSoup(html.content, 'html.parser')
            getExterLinks(bs, domain1)
            getInterLinks(bs, domain1)


def getAllLinks(url):
    global num
    #     html = urlopen(url)
    header = {
        'User-Agent': user_agent(),
    }
    html = requests.get(url, headers=header)
    time.sleep(random.random() * 3)  # 模拟人类行为，间隔随机的时间
    domain = '{}://{}'.format(urlparse(url).scheme, urlparse(url).netloc)
    bs = BeautifulSoup(html.content, 'html.parser')

    getInterLinks(bs, domain)
    getExterLinks(bs, domain)
    deepLinks()


def main():
    # 1. 定义命令行解析器对象
    parser = argparse.ArgumentParser(description='Demo of argparse')

    # 2. 添加命令行参数
    parser.add_argument('-u', '--url', dest='url', type=str, default='127.0.0.1', help='target User')

    # 3. 从命令行中结构化解析参数
    args = parser.parse_args()
    print(args)
    url = args.url
    getAllLinks(url)
    # print('show {}  {}'.format(epochs, batch))
    # with tqdm(total=len(urls_data)) as pbar:
    #     with ThreadPoolExecutor(max_workers=100) as ex:
    #         futures = [ex.submit(write, url, pbar) for url in urls_data]
    # end = time.time()
    # print("已生成完毕，总耗时:", end - start, "秒")


if __name__ == '__main__':
    main()
