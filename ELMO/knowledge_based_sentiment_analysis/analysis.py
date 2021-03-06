#-*- coding: utf-8 -*-

# Developer : Jeong Wooyoung , Park Jaesang
# Contact   : gunyoung20@naver.com  , kw0095@naver.com

from sklearn.cluster import DBSCAN
import re, sys

from storage_handler import StorageHandler
import time
import tensorflow_hub as hub
import tensorflow as tf
import os
import warnings

import logging
warnings.filterwarnings(action='ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
sh = StorageHandler()

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
tf.get_logger().setLevel(logging.ERROR)
tf.autograph.set_verbosity(1)


#########################################################################################################
# Viewer
#########################################################################################################
def progressBar(value, endvalue,  bar_length=60):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rCalculating practice: [{0}] {1}% ".format(arrow + spaces, int(round(percent * 100)) ))
    #sys.stdout.flush()
def progressBarwith_time(value, endvalue, start_time, bar_length=60):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rCalculating practice: [{0}] {1}%  {2}sec".format(arrow + spaces, int(round(percent * 100)),time.time()-start_time ))
    #sys.stdout.flush()
    

#########################################################################################################
# calculation
#########################################################################################################
def clustering(vectors):
    word_vectors = vectors['word_vectors']
    num_of_words = vectors['num_of_words']

    word_set = [word for word in word_vectors.keys()]
    vec_set = [word_vectors[word] for word in word_set]
    cluster = DBSCAN(min_samples=5, metric='cosine')
    labels = cluster.fit_predict(vec_set)

    cluster_group = {}
    for label, word in zip(labels, word_set):
        if label in cluster_group.keys():
            cluster_group[label][word] = num_of_words[word]
        else:
            cluster_group[label] = {word:num_of_words[word]}

    return cluster_group

def selectUsableWords(cluster_group, max_select=5):
    selected_words = []
    for label in cluster_group.keys():
        sorted_by_count = sorted(cluster_group[label].items(), key=(lambda x:x[1]), reverse=True)

        words_in_group = []
        for w in sorted_by_count:
            if len(w[0]) > 1: words_in_group.append(w[0])
            # words_in_group.append(w[0])
        if len(words_in_group) > max_select: selected_words += words_in_group[:max_select]
        else: selected_words += words_in_group
    return selected_words

def getSentimentScoreOnSelectedWords(tokenized_contents, selected_words):
    total = len(tokenized_contents)
    one_per = int(total/100)

    senti_dict = sh.getSentiDictionary()

    # ?????? ????????? ????????? ???????????? ??????????????? ????????????, ????????????
    senti_words = {}
    for i, t_content in enumerate(tokenized_contents):
        # ?????? ????????? ????????? ?????? ?????? ??????
        selected_words_in_sentence = []
        # token list??? sentence ???????????? ??????
        sentence = ''
        for word in t_content:
            sentence += word+' '
            if word in selected_words: selected_words_in_sentence.append(word)
        sentence = sentence[:-1]

        # ??????????????? ?????? ????????? ?????? ????????? ?????????????????? ?????? ?????? ?????? ??? ?????? ?????? ?????? ??????
        score = {'P':0.0, 'N':0.0, 'total':0.0}
        count = {'P':0, 'N':0, 'total':0}
        # ????????? ????????? ?????? ?????? ??? ?????? ??????
        senti_words_in_sentence = {}
        for s in senti_dict.keys():
            match = re.search('[ ]?'+s+'[^ ]*', sentence)
            # ??????????????? ?????? ?????? s??? ?????? ????????? ??????
            if not match is None:
                if senti_dict[s] > 0:
                    score['P'] += senti_dict[s]
                    count['P'] += 1
                elif senti_dict[s] < 0:
                    score['N'] += senti_dict[s]
                    count['N'] += 1

                score['total'] += senti_dict[s]
                count['total'] += 1

                senti_words_in_sentence[s] = {'score':senti_dict[s], 'count':1}

        # ?????? ????????? ????????? ???????????? ?????? ????????? ???????????? ??????
        for word in selected_words_in_sentence:
            if word in senti_words.keys():
                senti_words[word]['score']['P'] += score['P']
                senti_words[word]['score']['N'] += score['N']
                senti_words[word]['score']['total'] += score['total']

                senti_words[word]['count']['P'] += count['P']
                senti_words[word]['count']['N'] += count['N']
                senti_words[word]['count']['total'] += count['total']

                for w in senti_words_in_sentence.keys():
                    if w in senti_words[word]['related'].keys():
                        cnt = int(senti_words_in_sentence[w]['count'])
                        senti_words[word]['related'][w]['count'] += cnt
                    else:
                        senti_words[word]['related'][w] = senti_words_in_sentence[w]
            else:
                senti_words[word] = {'score':score.c,'count':count, 'related':senti_words_in_sentence}
        if (one_per>0):
            if (i+1)%one_per == 0:
                progressBar(i+1, total)
    # senti_words_in_sentence = {word:{'score':__score, 'count':__count}}
    # score = {'P':positive score, 'N':negative score, 'total':sum score}
    # count = {'P':positive count, 'N':negative count, 'total':sum count}
    # senti_words = {word:{'score':score,'count':count, 'related':senti_words_in_sentence}}
    return senti_words


#######################################################################################################################




# return ?????? vectors
def getElmoVector(contents , first):
    start_time = time.time()
    vectors = {  'word_vectors': {}, 'num_of_words' : {}}
    total = len(contents)
    file = open("./stopwords.txt", "r")
    stop_list = file.read().split()

    one_per = int(total/100)
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
	    # Currently, memory growth needs to be the same across GPU
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        except RuntimeError as e:
            print(e)
        # Memory growth must be set before GPUs have been initialized
    embed = hub.load("https://tfhub.dev/google/elmo/3")
    for num,temp in enumerate(contents):
        
        # t : ????????? ?????????+????????? corpus??? tokenized??? word list  ex) ['??????','???','??????']
        sentence = ''
        t = []
        
        for word in temp:
            
        # t??? string????????? ???????????? ????????????, ????????? ??????
            if word in stop_list:
                continue
            sentence+= word+' '
            t.append(word)
        # ????????? ????????? vectors??? ??????
        
        
        tf_sentence = tf.constant([sentence])
        #print(len(temp))
        try:
            sentence_output = embed.signatures['default'](tf_sentence)
            sentence_vec = sentence_output['word_emb']
        except :
            continue
        #print(sentence_vec.shape)
        
        # sentence_vec = [ v1,v2,v3,.......vn] , v1??? temp[1]??? ?????? vector???
        
        for index,word in enumerate(t):
            if word not in vectors['word_vectors']: vectors['word_vectors'][word] = sentence_vec[0][index]; vectors['num_of_words'][word]=1
            else:
                if first:
                    # ??? ?????? ????????? ???????????? ??????, vectors['word_vectors']??? ?????? ???????????? ?????? ??????
                    vectors['num_of_words'][word]+=1
                else:
                    #????????? ????????? ???????????? ??????
                    vectors['word_vectors'][word] = sentence_vec[0][index]; vectors['num_of_words'][word]+=1
        if (one_per>0):
            progressBar(num+1, total)
        
    # ??? vector?????? .numpy()??? ?????? float??? ????????????
    # vectors = {  'word_vectors': [], 'num_of_words' : []}
    # embeding ???, vectors['word_vectors'][word] ??? ??????
    # ??? ?????? ????????? ???????????? ??????,
    # if word not in vectors['word_vectors']: vectors['word_vectors'][word] = embeding ; vectors['num_of_words'][word] = 1
    # else: vectors['num_of_words'][word]+=1
    # ????????? ????????? ???????????? ??????,
    # if word not in vectors['word_vectors']: vectors['word_vectors'][word] = embeding ; vectors['num_of_words'][word] = 1
    # else: vectors['word_vectors'][word] = embeding ; vectors['num_of_words'][word]+=1
        


    print("Vectorizing time : ",end='')
    print(time.time() - start_time,end='')
    print(" sec")
    return vectors




########################################################################################################################




def getElmoScore(contents,keyword,num_of_words):
    # to use GPU
    start_time = time.time()
    total = len(contents)
    file = open("./stopwords.txt", "r")
    stop_list = file.read().split()

    one_per = int(total/100)
    result = {}
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
	    # Currently, memory growth needs to be the same across GPU
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        except RuntimeError as e:
            #print(e)
            pass
        # Memory growth must be set before GPUs have been initialized
    senti_dict = sh.getSentiDictionary()

    tf_keyword= tf.constant([keyword])
    embed = hub.load("https://tfhub.dev/google/elmo/3")
    keyword_output = embed.signatures['default'](tf_keyword)
    keyword_vec = keyword_output['word_emb']
    #output['word_emb'][0][0]-output1['word_emb'][0][0]
    for num,temp in enumerate(contents):
        
        # t : ????????? ?????????+????????? corpus??? tokenized??? word list  ex) ['??????','???','??????']
        sentence = ''
        t = []
        word_in_sentence={}
        for word in temp:
        # t??? string????????? ???????????? ????????????, ?????? ????????? ??????
            if word in stop_list:
                continue
            if word in num_of_words.keys():
                num_of_words[word]+=1
            else:
                num_of_words[word]=1
            sentence+= word+' '
            t.append(word)
        # ???????????? / keyword?????? ????????? ?????? ?????? ??????    
        tf_sentence = tf.constant([sentence])
        try:
            sentence_output = embed.signatures['default'](tf_sentence)
            sentence_vec = sentence_output['word_emb']
        except: #????????? ?????? ??? ?????? ( ????????? ?????? ??? ?????? ) ?????? ??????... ?????? ?????? ??????
            continue
        score = {'total':0.0,'p':0.0,'n':0.0}
        count = {'total':0,'p':0,'n':0}
        for i in range(0,len(t)):
            if t[i] in senti_dict.keys():
                temp = (keyword_vec[0][0]-sentence_vec[0][i])
                temp *= temp
                temp_distance = 0
                for d in temp:
                    temp_distance += d.numpy()
                senti_score = senti_dict[t[i]]
                if senti_score>0:
                    score['p'] += senti_score/temp_distance
                    count['p']+=1
                else:
                    score['n'] += senti_score/temp_distance
                    count['n']+=1
                score['total'] += senti_dict[t[i]]/temp_distance
                count['total']+=1
                if t[i] in word_in_sentence.keys():
                    word_in_sentence[t[i]]['count']+=1
                else:
                    word_in_sentence[t[i]] = {'score': senti_dict[t[i]], 'count':1}
        # ??? ????????? (???????????? / ?????? )??? ?????? ??????????????? score update
        for word in t: # t : ???????????? ????????? ?????? ?????? : t
            if word in result.keys() and word not in stop_list:
                score2 = score.copy(); count2 = count.copy()
                result[word]['score']['p']+= score2['p']
                result[word]['score']['n']+= score2['n']
                result[word]['score']['total']+= score2['total']
                result[word]['count']['p']+= count2['p']
                result[word]['count']['n']+= count2['n']
                result[word]['count']['total']+= count2['total']
                # ?????? ????????????, 
                
                for w in word_in_sentence:
                    if w in result[word]['related'].keys():
                        #cnt = int( word_in_sentence[w]['count'])
                        result[word]['related'][w]['count'] += 1
                    else:
                        result[word]['related'][w] = word_in_sentence[w].copy()
            else:
                score2 = score.copy(); count2 = count.copy()
                word2 = word_in_sentence.copy()
                result[word] = { 'score':{'total':score2['total'],'p':score2['p'],'n':score2['n']}, 'count':{'total':count2['total'],'p':count2['p'],'n':count2['n']} , 'related': word2  }
            
        if (one_per>0):
            progressBarwith_time(num+1, total,start_time)
    print("Total # "+str(total)+" sentences.")
    
    print("Vectorizing and calculating time : ",end='')
    print(time.time() - start_time,end='')
    print(" sec")
    return result
