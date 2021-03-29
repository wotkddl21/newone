FROM python:3
ADD * /
RUN pip install Scrapy
RUN pip install lxml
RUN pip install BeautifulSoup4
RUN pip install cfscrape
RUN pip install --upgrade google-api-python-client
RUN pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
RUN pip install selenium
RUN pip install numpy
CMD ["python","./main.py","홈트"]

