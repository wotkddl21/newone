#-*- coding: utf-8 -*-

# Developer : Jeong Wooyoung, EGLAB, Hongik University
# Contact   : gunyoung20@naver.com
import sys
import multiprocessing
from crawling_handler import CrawlingHandler
from multi_processor import MultiCrawler


if __name__ == '__main__' :
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()

        mc = MultiCrawler()
        ch = CrawlingHandler()
        keywords = ['홈트']

        for keyword in keywords:
            # mc.multiCrawlingYoutube(keyword)
            uids, videos = ch.youtube_list_crawling(keyword)
            print("Youtube Comments for '%s' crawling start. youtube ids count : %d"%(keyword, len(uids)))
            for uid in uids:
                print("Youtube id(%s) Comments crawling start. " % (uid))
                comments = ch.youtube_comments_crawling(uid)
                if comments is None :
                    print('Error occur from youtube id : ' + uid)
                elif len(comments) > 0:
                    ch.sh.saveYoutubeCom(keyword + '/%s'%(uid), comments)
                    print("Youtube id(%s) Comments %d crawling done. " % (uid, len(comments)))
                else:
                    print('Not have comments into youtube id : '+uid)
                print("Youtube id(%s) Comments crawling finish. " % (uid))
            print("Youtube Comments for '%s' crawling finish. youtube ids count : %d"%(keyword, len(uids)))
                # print(comments)
