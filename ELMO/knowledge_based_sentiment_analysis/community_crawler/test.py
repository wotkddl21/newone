import re
contents = ['a','b','c','d']
i=4
while True:
    print(len(contents))
    if i == len(contents):
        break
a = 'repItm repBg0 '
print(re.match(r'repItm.+',a))

#디버깅 크롬과 연결하기 위한 selenium 코드
from selenium import webdriver
from selenium.webdriver.chrome.options import options

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
