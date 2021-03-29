from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib
from bs4 import BeautifulSoup
import cfscrape
import re, time
import datetime

from multiprocessing import Lock
from storage_handler import StorageHandler
from scraper import Scraper

import requests, argparse, json
import lxml.html
import io

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sys
import pyperclip

import random


import uuid
import rsa
import lzstring
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from file_handler import FileHandler



from lxml.cssselect import CSSSelector


def progressBar(value, endvalue,  bar_length=60):

    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rCalculating practice: [{0}] {1}% ".format(arrow + spaces, int(round(percent * 100)) ))
def find_value(html, key, num_chars=2):
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find('"', pos_begin)
    return html[pos_begin: pos_end]
def extract_comments(html):
    tree = lxml.html.fromstring(html)
    item_sel = CSSSelector('.comment-item')
    text_sel = CSSSelector('.comment-text-content')
    #text_sel = CSSSelector('.content-text')
    
    time_sel = CSSSelector('.time')
    author_sel = CSSSelector('.user-name')
#content-text
    for item in item_sel(tree):
        yield {'cid': item.get('data-cid'),
               'text': text_sel(item)[0].text_content(),
               'time': time_sel(item)[0].text_content().strip(),
               'author': author_sel(item)[0].text_content()}
def extract_reply_cids(html):
    tree = lxml.html.fromstring(html)
    sel = CSSSelector('.comment-replies-header > .load-comments')
    return [i.get('data-cid') for i in sel(tree)]
def ajax_request(session, url, params, data, retries=10, sleep=20):
    for _ in range(retries):
        response = session.post(url, params=params, data=data)
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            return response_dict.get('page_token', None), response_dict['html_content']
        else:
            time.sleep(sleep)
def contents_limit(contents):
    #limit_length = 131072
    limit_length = 20000
    contents = contents.replace('\n','.')
    temp = [ contents[i:i+limit_length] for i in range(0,len(contents),limit_length)]
    return temp


class CrawlingHandler :
    def __init__(self):
        self.lock = Lock()
        self.sh = StorageHandler()
        self.scraper = cfscrape.create_scraper()
        self.browser_scraper = Scraper()
    def quote(self, text): return urllib.parse.quote(text) #한글 텍스트를 퍼센트 인코딩하기
    def progressBar(self,value, endvalue,bar_length=60):
        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length)-1) + '>'
        spaces = ' ' * (bar_length - len(arrow))
        sys.stdout.write("\rCalculating practice: [{0}] {1}%  ".format(arrow + spaces, int(round(percent * 100)), ))
    def getResponse(self, address):
        for i in range(0, 100):
            try:
                response = self.scraper.get(address)
            except :
                time.sleep(1)
                continue
            return response
        return None
    def parseContents(self, contents):
        contents = contents.replace('\r','').replace('\t',' ').replace('#','')
        contents = re.sub('[ ]+',' ',contents)
        split = contents.split('\n')
        contents = ''
        for temp in split:
            contents += temp.strip()+'\n'
        contents = re.sub('^[\n]+|[\n]+$', '', contents)
        contents = re.sub('([ ]?[\n][ ]?){2,}', '\n\n', contents)

        contents = re.sub('[a-zA-Z\-_.]+[ ]?=[ ]?[a-zA-Z\-_.]+[ ][|]+[ ][(){}\[\] ]+;[\n]?', '', contents)
        contents = re.sub('[a-zA-Z\-_.]+[\[({]+[\n]?', '', contents)
        contents = re.sub('[a-zA-Z\-_.]+[ ]?:[ ]?[a-zA-Z\-_.\' ]+[,]?[\n]?', '', contents)
        contents = re.sub('[)}\]]+;[\n]?', '', contents)
        contents = re.sub('^[\n]+|[\n]+$', '', contents)

        return contents
    '''
    def template_list_crawling(self,keyword):
       return docs [url,title]
    def template_doc_crawling(self,document):
       return document  [url,title,time,author,contents]
    def template_docs_crawling(self, process, keyword, docs):
        sys.stdout.flush()
        count = 1
        total = len(docs)
        print("Process "+str(process)+"  Documents crawling start. documents count : "+str(total))
        for doc in docs:
            document = self.template_doc_crawling(doc)
            if document and len(document) >4:
                count += 1
                with self.lock:
                    self.sh.savetemplateDoc(keyword, document)
#            else:
#                print('Error occur from template site : '+doc[0])
        return
    '''


    