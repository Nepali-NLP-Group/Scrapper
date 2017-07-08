# -*- coding: utf-8 -*-
import sys
import bs4 as bs
import urllib
import re

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

    def extractContent(self):
        r = urllib.urlopen(self.NEWS_LINK).read()
        soup = bs.BeautifulSoup(r)
        return self.parseContent(soup)

    def parseContent(self, content):
        print ("====================== DISPLAYING THE CONTENTS ======================")
        self.extractCategory(content)

    def extractCategory(self, content):
        categoryOriginal = {}
        categories = {}

        for paragraph in content.find_all('a'):
            link = paragraph.get('href')

            if link is not None:

                match = re.match(r'/category/', link, re.M | re.I)
                if match:
                    categoryOriginal[paragraph.get('href').replace("/category/", "")] = paragraph.text

        # {category , category_text}
        #remove redundant category
        for key, value in categoryOriginal.items():
            if key not in categories.keys():
                categories[key] = value
        self.extractHeadline(categories)


    # retrieve headline for each category
    def extractHeadline(self, categoryList):

        for category, category_value in categoryList.items():
            url = ''
            url = url.join((self.NEWS_LINK, '/category/', category))

            print (
            "################################### Category : %s ###################################" % (category_value))
            r = urllib.urlopen(url).read()
            soup = bs.BeautifulSoup(r)

            headlineList = []
            for data in soup.find_all('div', {'class': ['item-wrap', 'wrap']}):
                if data.find('a') is not None:
                    # verify that it is content page
                    if 'html' in data.find('a').get('href'):
                        headlineList.append(data.find('a').get('href'))

            self.newsContents(headlineList)

    # retrieve the body for each headline
    def newsContents(self, headlineList):

        for index, headline in enumerate(headlineList):
            print ("*********************************** Headline : %s **********************************" % (index + 1))
            url = ''
            url = url.join((self.NEWS_LINK, headline))
            r = urllib.urlopen(url).read()
            soup = bs.BeautifulSoup(r)

            title_source = soup.find_all('div', {'class': ['wrap', 'content-wrapper', 'maincontent']})

            for title_ in title_source:
                if title_.find({'h1', 'h2'}) is not None:
                    self.TITLE = title_.find({'h1', 'h2'}).text

            body_content = soup.find('div', {'class': 'content-wrapper'})
            print ("Title : " + self.TITLE)
            scrapper = Scrapper()
            for body in body_content.find_all('p'):
                # check if it the body is empty
                # exclude the javascript inside <p></p> tag
                if str(body.text.encode('ascii', 'ignore'))!=""  and 'script' not in str(body):
                    scrapper.BODY += body.text
            self.BODY = scrapper.BODY
            print ("Body : " + self.BODY)

def main():
    news_link = sys.argv[1]
    news_source_name = sys.argv[2]
    Scrapper(news_link=news_link, source=news_source_name).extractContent()


if __name__ == '__main__':
    main()
