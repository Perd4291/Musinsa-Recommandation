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
pants_list = []

# 상품번호
file_name = "pants_nums.txt"
file_open = open(file_name, "w", encoding="utf-8")

for page in range(1, 11):
    if ((page % 2) == 1):
        sleep(random.uniform(3, 4))
    url = "https://search.musinsa.com/category/003?&page="+str(pagenum+1)
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")
    r = re.compile('#pol([0-9]+)')
    pantss = soup.find_all("a", attrs={"href": r})
    for pants in pantss:
        pants_num = ''.join(r.findall(pants['href']))
        pants_list.append({'pants_num': pants_num})
        file_open.write(pants_num+' ')
    pagenum += 1
file_open.close()


# 상품번호로 상품 정보 가져오기 시작
for pants in pants_list:
    breaknum += 1
    if(breaknum % 10 == 0):
        sleep(random.uniform(4, 5))
        print("breaking", breaknum)

    url = "https://store.musinsa.com/app/goods/"+str(pants['pants_num'])
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")

    # 상품 이름
    pants_temp = soup.select('span.product_title em')
    temp = re.sub('<.+?>', '', str(pants_temp), 0, 0).strip()
    pants_name = temp[1:-1]
    pants.update(pants_name=pants_name)

    # 상품 브랜드
    pants_brand_tag = soup.select('p.product_article_contents strong a')
    pants_brand_remove_tag = re.sub(
        '<.+?>', '', str(pants_brand_tag), 0, 0).strip()
    pants_brand = pants_brand_remove_tag[1:-1]
    pants.update(pants_brand=pants_brand)

    # 상품 해시태그
    pants_hashtag_tag = soup.select('p.product_article_contents a.listItem')
    pants_hashtag_remove_tag1 = re.sub(
        '<.+?>', '', str(pants_hashtag_tag), 0, 0).strip()
    pants_hashtag_remove_tag = re.sub(
        ',', '', pants_hashtag_remove_tag1, 0, 0).strip().replace(" ", '')
    pants_hashtag = pants_hashtag_remove_tag[1:-1]
    pants.update(pants_hashtag=pants_hashtag)

    # 상품 별점
    pants_temp = soup.select('span.prd-score__rating')
    temp = re.sub('<.+?>', '', str(pants_temp), 0, 0).strip()
    pants_starrating = temp[1:-1]
    pants.update(pants_starrating=pants_starrating)

    # 상품 이미지 주소
    pants_image_tag = str(soup.select('div.product-img img#bigimg'))
    a = (pants_image_tag.find('src'))+5
    b = (pants_image_tag.find('title'))-2
    imgUrl = "https:"+pants_image_tag[a:b]
    pants.update(pants_imgUrl=imgUrl)

    # 상품 구매 횟수
    headers = {
        'referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    url = 'https://m.store.musinsa.com/app/product/goodsview_stats/' + \
        str(pants_num)+'/0?&menu=view'
    response = urlopen(Request(url, headers=headers)).read().decode('utf-8')
    rank_json_int = json.loads(response)['purchase']['total_categories']
    rank_json = str(rank_json_int)  # 총 구매 횟수
    pants.update(pants_rank=rank_json)


sleep(random.uniform(1, 2))


# 상품 좋아요
new_int_pants_nums = []

for pants in pants_list:
    pants_num = int(pants["pants_num"])
    new_int_pants_nums.append(pants_num)

headers = {
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
}

data = '{"relationIds":'+str(new_int_pants_nums)+'}'

response = requests.post(
    'https://like.musinsa.com/like/api/v2/liketypes/goods/counts', headers=headers, data=data)

counttext = response.text.replace('"count":', 'count').split(',')
counttemp = [word for word in counttext if'count' in word]
countheart = re.sub('count', '', str(counttemp), 0, 0)[1:-1]
pants_hearts = re.sub(r"[^,0-9]", "", countheart).split(',')

i = 0
for pants in pants_list:
    pants.update(pants_hearts_count=pants_hearts[i])
    i += 1

# json 데이터 출력
with open('musinsa_pantss.json', 'a', encoding="utf-8") as f:
    f.write(json.dumps(pants_list))

print(time.time() - start)