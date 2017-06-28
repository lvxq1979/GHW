# coding=utf-8

import urllib
from bs4 import BeautifulSoup
from collections import deque
import threading
import pymysql
import os

url_queue = deque()
visited_urls = set()
crawled_cars = set()
lock = threading.Lock()
base_imgs_path = "/home/lvxq/Downloads/cars"


def crawl_page(url):
    global count
    print("Now crawing " + str(count) + ":" + url)
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    ret_val = response.read().decode("utf-8")
    return ret_val

def parse_page_sub_links(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all('a', {"rrc-event-param": "search", "target": "_blank"})

def parse_page_car_information(html, url):
    soup = BeautifulSoup(html, "html.parser")
    car_id = soup.find('p', {"class" : "detail-car-id"}).string.strip().strip('车源号：')
    car_keyword = soup.find('meta', {'name' : 'keywords'}).get('content')
    car_description = soup.find('meta', {'name' : 'description'}).get('content')
    return [car_id, car_keyword, car_description, url]

def download_car_pictures(html, car_id, car_db_id):
    soup = BeautifulSoup(html, "html.parser")
    img_list = soup.find_all('img', {"class" : "main-pic"})
    for img in img_list:
        img_url = "https:" + img.get("src")
        idx = img_url.find('?')
        if idx >= 0:
            img_url = img_url[0: idx]
        dst_dir = base_imgs_path + "/" + car_id
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        idx = img_url.find('/')
        img_name = img_url
        if idx >= 0:
            img_name = img_url[idx:]
        img_path = dst_dir + '/' + img_name
        urllib.request.urlretrieve(img_url, img_path)
    pass

def save_car_info_to_db(car_information):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1234', db='mycars', use_unicode=True,
                           charset='utf8')
    cur = conn.cursor()
    try:
        cur.execute('SELECT id FROM carlist WHERE carid=%s', (car_information[0]))
        cur.fetchall()
        if (cur.rowcount > 0):
            return
        else:
            cur.execute('INSERT INTO carlist(carid, keywords, description, url) VALUES(%s, %s, %s, %s)',
                                 (car_information[0], car_information[1], car_information[2], car_information[3]))
            conn.commit()
    except Exception:
        return
    finally:
        cur.close()
        conn.close()


def crawl_sub_page(url):
    global count
    count += 1
    html = crawl_page(url)

    global lock
    lock.acquire()
    global visited_urls
    visited_urls.add(url)
    lock.release()

    new_cars_list = parse_page_sub_links(html)
    car_infos = parse_page_car_information(html, url)
    lock.acquire()
    save_car_info_to_db(car_infos)
    global url_queue
    for new_car in new_cars_list:
        new_car_url = "https://www.renrenche.com/" + new_car.get("href")
        if not new_car_url in visited_urls:
            url_queue.append(new_url)
            print("New URL: " + new_url)
    lock.release()
    download_car_pictures(html, car_infos[0], 0)



url = "https://www.renrenche.com/bj/ershouche/le-xiao_pr-3-5_ge-s/?ge=s&le=xiao_jin&pr=3-5&plog_id=66a0dd473f1494ca8130f138afbe4890"
count = 1;
content = crawl_page(url)
visited_urls.add(url)

cars_list = parse_page_sub_links(content)
for car in cars_list:
    new_url = "https://www.renrenche.com/" + car.get("href")
    if not new_url in visited_urls:
        url_queue.append(new_url)
        print("New URL: " + new_url)

while len(url_queue) > 0:
    try:
        url = url_queue.pop()
        if url is None:
            break
        else:
            if url in visited_urls:
                continue
            else:
                thread = threading.Thread(target=crawl_sub_page, args=(url,))
                thread.start()
                thread.join(1)
    except:
        quit(0)

print("All cars crawled, exit!")


