# Musinsa-Recommandation

- 온라인 패션 쇼핑몰인 무신사에 상품 데이터를 이용한 추천 시스템
- TF-IDF와 Word2Vec을 이용하여 사용자에게 추천

# Dependencies

- gensim == 3.2.0

# TF-IDF와 Word2Vec의 유사도 계산
```python
#TF-IDF
tfidf = TfidfVectorizer(min_df = 1, ngram_range=(1,3))
tf_sim=cosine_similarity(tag_tf,tag_tf)
tf_euc=euclidean_distances(tag_tf,tag_tf)
tf_man=manhattan_distances(tag_tf,tag_tf)

#Word2Vec
word2vec_model = Word2Vec(size = 300, window = 5, min_count = 2, workers = 2)
w2v_sim = cosine_similarity(hashtag_embedding_list, hashtag_embedding_list)
w2v_euc = euclidean_distances(hashtag_embedding_list,hashtag_embedding_list)
w2v_man = manhattan_distances(hashtag_embedding_list,hashtag_embedding_list)
'''
