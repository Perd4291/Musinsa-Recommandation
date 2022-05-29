import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import manhattan_distances
import matplotlib.pyplot as plt
import urllib.request
import requests
from PIL import Image
from io import BytesIO

#데이터 전처리
df_pants = pd.read_csv('data\musinsa_pants.csv', encoding = 'cp949')
df_top = pd.read_csv('data\musinsa_top.csv', encoding = 'cp949')

df_pants.rename(columns = {"pants_num":"number", "pants_name":"name", "pants_brand":"brand", "pants_hashtag":"hashtag", "pants_starrating":"starrating", "pants_imgUrl":"imgUrl", "pants_rank":"rank", "pants_hearts_count":"hearts_count"}, inplace=True)
df_top.rename(columns = {"top_num":"number", "top_name":"name", "top_brand":"brand", "top_hashtag":"hashtag", "top_starrating":"starrating", "top_imgUrl":"imgUrl", "top_rank":"rank", "top_hearts_count":"hearts_count"}, inplace=True)

df = pd.concat([df_pants, df_top])

df.hashtag = df.hashtag.str.replace('#',' ')

df['name'] = df.name.str.replace(r'\[[^)]*\]', '')
df['name'] = df.name.str.replace(r'\([^)]*\)', '')
df['name'] = df.name.str.strip()
df = df.drop_duplicates(['name'])

df['hashtag'].replace('', np.nan, inplace=True)
df = df[df['hashtag'].notna()]
df.reset_index(drop=True, inplace=True)

#TF-IDF

tfidf = TfidfVectorizer(min_df = 1, ngram_range=(1,3))
tag_tf = tfidf.fit_transform(df['hashtag'])

tf_sim=cosine_similarity(tag_tf,tag_tf)
tf_euc=euclidean_distances(tag_tf,tag_tf)
tf_man=manhattan_distances(tag_tf,tag_tf)

#Word2Vec
corpus = []
for words in df['hashtag']:
    corpus.append(words.split())

word2vec_model = Word2Vec(size = 300, window = 5, min_count = 2, workers = 2)
word2vec_model.build_vocab(corpus)
word2vec_model.train(corpus, total_examples = word2vec_model.corpus_count, epochs = 15)

def hashtag_vectors(hashtag_list):
    hashtag_embedding_list = []
    
    for line in hashtag_list:
        
        doc2vec = None
        count = 0
        
        for word in line.split():
            if word in word2vec_model.wv.vocab:
                count += 1
                
                if doc2vec is None:
                    doc2vec = word2vec_model[word]
                else:
                    doc2vec = doc2vec + word2vec_model[word]
                    
        if doc2vec is not None:
            doc2vec = doc2vec / count
            hashtag_embedding_list.append(doc2vec)
            
    return hashtag_embedding_list

hashtag_embedding_list = hashtag_vectors(df['hashtag'])

w2v_sim = cosine_similarity(hashtag_embedding_list, hashtag_embedding_list)
w2v_euc = euclidean_distances(hashtag_embedding_list,hashtag_embedding_list)
w2v_man = manhattan_distances(hashtag_embedding_list,hashtag_embedding_list)

df = df.iloc[0:1441,]


# 비슷한 상품 상위 5개를 
def recommendations(name, similarity):
    clothes = df[['name', 'imgUrl']]
    
    indices = pd.Series(df.index, index = df['name']).drop_duplicates()    
    idx = indices[name]
    
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)
    sim_scores = sim_scores[1:6]
    
    clothe_indices = [i[0] for i in sim_scores]
    
    recommend = clothes.iloc[clothe_indices].reset_index(drop=True)
    
    fig = plt.figure(figsize=(30, 40))
    plt.rc('font', family='Malgun Gothic')

    for index, row in recommend.iterrows():
        response = requests.get(row['imgUrl'])
        img = Image.open(BytesIO(response.content))
        fig.add_subplot(1, 5, index + 1)
        plt.imshow(img)
        plt.title(row['name'])

    plt.show() 

input = '원턱 와이드 스웨트팬츠 그레이'
input2 = '화란 세미오버 니트 라벤더'
recommendations(input2, tf_sim)
