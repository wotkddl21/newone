# coding: utf-8

# Developer : Jeong Wooyoung
# Contact   : gunyoung20@naver.com

from datetime import datetime

import analysis

from vectorizer import Vectorizer
from storage_handler import StorageHandler

if __name__ == '__main__':
    # Load Data
    sh = StorageHandler()
    target = '한의원'
    contents = sh.getContents(target)

    # Vectorizing
    using_dict = False
    vec = Vectorizer()
    model_path = 'models/word2vec_ko.model'
    # vectors = {'word_vectors':word_vectors(list), 'vectorized_contents':vectorized_contents(list), 'num_of_words':num_of_words(dict}
    print('Vectorizing Start. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))
    vectors = vec.vectorize(model_path, contents, dims=100, using_dict=using_dict, training=False, padding=False)
    print('Vectorizing Finish. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))
    word_vectors = vectors['word_vectors']
    num_of_words = vectors['num_of_words']

    # Clustering
    print('Clustering Start. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))
    # vectors = {word_vectors, num_of_words, vectorized_contents}
    cluster_group = analysis.clustering(vectors)
    print('Clustering Finish. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))

    # select words
    max_select = 5
    selected_words = analysis.selectUsableWords(cluster_group, max_select=max_select)
    print('Done select words. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))

    # Sentiment Analysis
    tokenized_contents = vec.tokenizing(contents)
    print('Calculating Sentiment Start. %d sentences (%s)'%(len(tokenized_contents), datetime.now().strftime('%m-%d %H:%M:%S.%f')))
    # senti_words = {word:{'score':score,'count':count, 'related':senti_words_in_sentence}}
    senti_words = analysis.getSentimentScoreOnSelectedWords(tokenized_contents, selected_words)
    print('\nCalculating Sentiment Finish. (%s)'%(datetime.now().strftime('%m-%d %H:%M:%S.%f')))

    sh.saveSentiWords(selected_words, num_of_words, senti_words, file=target)

    print(senti_words)
    # related = {'소모':{'score':231.0, 'count':25},
    #            '역시':{'score':-23.0, 'count':32},
    #            '배선':{'score':800.0, 'count':1345}}
    # st_words = sorted(related.items(), key=(lambda x: x[1]['count']), reverse=True)
    # lines = ['%s(%f, %d)' % (rw, info['score'], info['count']) for rw, info in st_words]
    # print(st_words)