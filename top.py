from urllib.request import urlopen, Request
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import re
from time import sleep
import random
import time


start = time.time()

pagenum = 0
breaknum = 0
top_list = []

# 상품번호
file_name = "top_nums.txt"
file_open = open(file_name, "w", encoding="utf-8")

for page in range(1, 11):
    if ((page % 2) == 1):
        sleep(random.uniform(3, 4))
    url = "https://search.musinsa.com/category/001?&page="+str(pagenum+1)
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")
    r = re.compile('#pol([0-9]+)')
    tops = soup.find_all("a", attrs={"href": r})
    for top in tops:
        top_num = ''.join(r.findall(top['href']))
        top_list.append({'top_num': top_num})
        file_open.write(top_num+' ')
    pagenum += 1
file_open.close()


# 상품번호로 상품 정보 가져오기 시작
for top in top_list:
    breaknum += 1
    if(breaknum % 10 == 0):
        sleep(random.uniform(4, 5))
        print("breaking", breaknum)

    url = "https://store.musinsa.com/app/goods/"+str(top['top_num'])
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")

    # 상품 이름
    top_temp = soup.select('span.product_title em')
    temp = re.sub('<.+?>', '', str(top_temp), 0, 0).strip()
    top_name = temp[1:-1]
    top.update(top_name=top_name)

    # 상품 브랜드
    top_brand_tag = soup.select('p.product_article_contents strong a')
    top_brand_remove_tag = re.sub(
        '<.+?>', '', str(top_brand_tag), 0, 0).strip()
    top_brand = top_brand_remove_tag[1:-1]
    top.update(top_brand=top_brand)

    # 상품 해시태그
    top_hashtag_tag = soup.select('p.product_article_contents a.listItem')
    top_hashtag_remove_tag1 = re.sub(
        '<.+?>', '', str(top_hashtag_tag), 0, 0).strip()
    top_hashtag_remove_tag = re.sub(
        ',', '', top_hashtag_remove_tag1, 0, 0).strip().replace(" ", '')
    top_hashtag = top_hashtag_remove_tag[1:-1]
    top.update(top_hashtag=top_hashtag)

    # 상품 별점
    top_temp = soup.select('span.prd-score__rating')
    temp = re.sub('<.+?>', '', str(top_temp), 0, 0).strip()
    top_starrating = temp[1:-1]
    top.update(top_starrating=top_starrating)

    # 상품 이미지 주소
    top_image_tag = str(soup.select('div.product-img img#bigimg'))
    a = (top_image_tag.find('src'))+5
    b = (top_image_tag.find('title'))-2
    imgUrl = "https:"+top_image_tag[a:b]
    top.update(top_imgUrl=imgUrl)

    # 상품 구매 횟수
    headers = {
        'referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    url = 'https://m.store.musinsa.com/app/product/goodsview_stats/' + \
        str(top_num)+'/0?&menu=view'
    response = urlopen(Request(url, headers=headers)).read().decode('utf-8')
    rank_json_int = json.loads(response)['purchase']['total_categories']
    rank_json = str(rank_json_int)  # 총 구매 횟수
    top.update(top_rank=rank_json)


sleep(random.uniform(3, 4))


# 상품 좋아요
new_int_top_nums = []

for top in top_list:
    top_num = int(top["top_num"])
    new_int_top_nums.append(top_num)

headers = {
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
}

data = '{"relationIds":'+str(new_int_top_nums)+'}'

response = requests.post(
    'https://like.musinsa.com/like/api/v2/liketypes/goods/counts', headers=headers, data=data)

counttext = response.text.replace('"count":', 'count').split(',')
counttemp = [word for word in counttext if'count' in word]
countheart = re.sub('count', '', str(counttemp), 0, 0)[1:-1]
top_hearts = re.sub(r"[^,0-9]", "", countheart).split(',')

i = 0
for top in top_list:
    top.update(top_hearts_count=top_hearts[i])
    i += 1

# json 데이터 출력
with open('musinsa_tops.json', 'a', encoding="utf-8") as f:
    f.write(json.dumps(top_list))

print(time.time() - start)
