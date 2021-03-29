# coding: utf-8

from datetime import datetime

import analysis
import sys
from vectorizer import Vectorizer
from storage_handler import StorageHandler
import time

if __name__ == '__main__':
    # Load Data
    sh = StorageHandler()
#    target = '홈트'
    target_list = sys.argv[1:]
#    target = sys.argv[1]
    
    for target in target_list:
    #    target = '트레이닝'
        now = time.localtime()
        start = time.time()
        print("start time : ",end='')
        print ("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
        contents = sh.getContents(target)
        
        #Elmo방식
        vec = Vectorizer()
        tokenized_contents = vec.tokenizing(contents)
        num_of_words = {}
        
        result = analysis.getElmoScore(tokenized_contents,target,num_of_words)
        result_time = time.time()-start
        save_time_start = time.time()
        sh.saveElmoWords(result, num_of_words,file=target)
        save_time_end = time.time()
        now = time.localtime()
        print("End time : ",end='')
        print ("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
        print("Total time : "+ str(time.time()-start)+"sec")
        print("Analysis time : " + str(result_time)+"sec")
        print("Save time : "+ str(save_time_end-save_time_start)+"sec")
    