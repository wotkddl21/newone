#-*- coding: utf-8 -*-

# Developer : Jeong Wooyoung, EGLAB, Hongik University
# Contact   : gunyoung20@naver.com

import sys
import multiprocessing
from datetime import datetime
from multi_processor import MultiCrawler
#include "user_header.h"


if __name__ == '__main__' :
    if sys.platform.startswith('linux'):
        print("argv[1] :"+sys.argv[1])
   # if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
        multiprocessing.set_start_method("spawn")
        mc = MultiCrawler()
#        keywords = ['홈트']

        keywords = sys.argv[1:]
#        keywords.append(sys.argv[1])
        
        #processes = [mc.multiCrawlingDaum]
        
        #processes = [mc.multiCrawlingFacebook,mc.multiCrawlingInsta,mc.multiCrawlingHygall, mc.multiCrawlingSlrclub,
        #       mc.multiCrawlingYgosu, mc.multiCrawlingHumoruniv, mc.multiCrawlingTheqoo, mc.multiCrawlingEtoland,
        #       mc.multiCrawlingFmkorea, mc.multiCrawlingPann, mc.multiCrawlingBobae, mc.multiCrawlingDcinside,
        #       mc.multiCrawlingRuliweb, mc.multiCrawlingMlbpark, mc.multiCrawlingInven, mc.multiCrawlingTodayhumor,
        #       mc.multiCrawlingPpomppu, mc.multiCrawlingClien, mc.multiCrawlingInstiz, mc.multiCrawlingCook82,mc.multiCrawlingNaver]
        
#        processes = [mc.multiCrawlingFacebook,mc.multiCrawlingInsta,mc.multiCrawlingHygall, mc.multiCrawlingSlrclub,mc.multiCrawlingNaver,
#               mc.multiCrawlingYgosu, mc.multiCrawlingHumoruniv, mc.multiCrawlingTheqoo, mc.multiCrawlingEtoland,
#               mc.multiCrawlingFmkorea, mc.multiCrawlingPann, mc.multiCrawlingBobae, mc.multiCrawlingDcinside,
#               mc.multiCrawlingRuliweb, mc.multiCrawlingMlbpark, mc.multiCrawlingInven, mc.multiCrawlingTodayhumor,
#               mc.multiCrawlingPpomppu, mc.multiCrawlingClien, mc.multiCrawlingInstiz, mc.multiCrawlingCook82]
        
        
        
 
        processes = [mc.multiCrawlingInsta]
        start = datetime.now()
        for keyword in keywords:
           community_start = datetime.now()
           print("Community "+keyword+" crawling start.")
           mc.distributeProcess(keyword, processes)
           sys.stdout.flush()
           print("Community "+keyword+" crawling finish. spend time :",(datetime.now()-community_start))
        
        print("Community crawling finish. spend time :",(datetime.now()-start)) 