# -*- coding: utf-8 -*-
import sys
import bs4 as bs
import re
import requests


class ReadOnlyClass(type):
    def __setattr__(self, name, value):
        raise ValueError(name)


class Scrapper:
    __metaclass__ = ReadOnlyClass

    def __init__(self, news_link='', source=''):
        self.NEWS_LINK = news_link
        self.SOURCE = source
        self.TITLE = ''
        self.BODY = ''


    def accessUrl(self, news_link):
        page = requests.get(news_link)
        soup = bs.BeautifulSoup(page.content, "html.parser")
        return soup

    def extractContent(self):
        return self.parseContent(self.accessUrl(self.NEWS_LINK))

    def parseContent(self, content):
        print ("====================== DISPLAYING THE CONTENTS ======================")
        self.extractCategory(content)

    def extractCategory(self, content):
        categoryOriginal = {}
        categories = {}

        for paragraph in content.find_all('li', {'class': ''}):

            link = paragraph.find('a')

            if link is not None:
                link = link.get('href')
                match = re.match(r'%s/newslist/' % (self.NEWS_LINK), link, re.M | re.I)
                if match:
                    categoryOriginal[link.replace("%s/newslist/" % (self.NEWS_LINK), "")] = paragraph.text

        # remove redundant category
        for key, value in categoryOriginal.items():
            if key not in categories.keys():
                categories[key] = value
        self.extractHeadline(categories)

    # retrieve headline for each category
    def extractHeadline(self, categoryList):

        for category, category_value in categoryList.items():
            url = ''
            url = url.join((self.NEWS_LINK, '/news/', category))
            print (
                "############################# Category : %s #############################" % (category_value))
            soup = self.accessUrl(url)

            headlineURLList = []
            for data in soup.find_all('div', {'class': 'row'}):
                if data.find('a') is not None:
                    headline_link_original = data.find('a').get('href')
                    match = re.match(r'%s/news/' % (self.NEWS_LINK), headline_link_original, re.M | re.I)
                    if match:
                        headlineURLList.append(headline_link_original)
            self.newsContents(headlineURLList)

    # retrieve the body for each headline
    def newsContents(self, headlineURLList):

        for index, headlineURL in enumerate(headlineURLList):
            print ("*********************************** Headline : %s **********************************" % (index + 1))
            Scrapper()

            soup = self.accessUrl(headlineURL)

            self.TITLE = soup.find('div', {'class': 'detailbox'}).find('h2', {'class': 'newstitle'}).text

            body = soup.find_all('div', {'class': 'detail_content'})
            scrapper = Scrapper()
            for b in body:
                for body_content in b.find_all('p', {'class': ""}):
                    if str(body_content.text.encode('ascii', 'ignore')) is not "":
                        scrapper.BODY += body_content.text
            self.BODY = scrapper.BODY
            print ("Title : " + self.TITLE)
            print ("Body : " + self.BODY)

def main():
    news_link = sys.argv[1]
    news_source_name = sys.argv[2]
    Scrapper(news_link=news_link, source=news_source_name).extractContent()


if __name__ == '__main__':
    main()
