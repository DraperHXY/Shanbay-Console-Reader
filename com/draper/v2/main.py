import sys
import os
import json
import requests
from xml.etree import ElementTree as ET

warning_start = '\033[1;35m'
warning_end = '\033[0m'


class ShanbayApi:
    def __init__(self):
        self.baseApi = 'https://www.shanbay.com/api/v2'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Cookie": "userid=82447108; auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ODI0NDcxMDgsImV4cCI6MTU5MjIxNDIwOCwiaXNfc3RhZmYiOjAsInVzZXJuYW1lIjoiZHJhcGVyX2h4eSIsImRldmljZSI6IiJ9.SUwWnj_5cSUY4UduO7MDNf_FtPq2zmOKwEglrnUvoSU"
        }
        self.rs = requests.session()

    def getArticlesOverview(self):
        url = self.baseApi + '/news/articles/'
        params = {
            'ipp': 10,
            'pageSize': 1
        }
        res = self.rs.get(url, params=params, headers=self.headers, verify=True)
        dicData = json.loads(res.text)
        return dicData['data']['objects']

    def printArticlesOverview(self):
        titles = []
        articelsInfos = self.getArticlesOverview()

        for line in articelsInfos:
            titles.append(Title(line['id'], line['title_en'], line['title_cn']))

        return titles

    def getArticleDetail(self, id):
        url = self.baseApi + '/news/articles/' + id + '/'

        cookies = {
            # 'auth_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6ODI0NDcxMDgsImV4cCI6MTU5MTYxMDQyNywiZGV2aWNlIjoiIiwidXNlcm5hbWUiOiJkcmFwZXJfaHh5IiwiaXNfc3RhZmYiOjB9.O6T-KNlOYjcrlMzFUrEtByDZROS4ToQomMXUA9UCfXk',
            # 'userId': '82447108',
            # 'csrftoken':'waqjbVgMKQ7ux6hCIj6jjZdTQBTWBvXO'
        }
        cookieStr = ''
        # for line in [key + '=' + cookies[key] + ';' for key in cookies]:
        #     cookieStr = cookieStr + line

        headers = {
            # 'cookie': line
        }
        res = self.rs.get(url, headers=self.headers, verify=True)
        assert res.status_code == 200
        dicData = json.loads(res.text)
        title = Title(dicData['data']['id'], dicData['data']['title_en'], dicData['data']['title_cn'])
        return (title, dicData['data']['content'])

    def readArticleFromXml(self, xmlStr):

        paragraphDics = {}

        root = ET.XML(xmlStr)
        for paraNode in root.iter('para'):
            content = ''
            for sentNode in paraNode.iter('sent'):
                content = content + '\t' + warning_start + sentNode.text + warning_end + '\n'
            paragraphDics[paraNode.get('id')] = content
        return paragraphDics

    def getInterpretation(self, id):

        url = self.baseApi + '/news/notes/?para_id=' + id + '&ipp=3&page=1'

        res = self.rs.get(url, headers=self.headers, verify=False)
        dicData = json.loads(res.text)
        if len(dicData['data']['objects']) != 0:
            return dicData['data']['objects'][0]['content']
        return None


class ReadSetting:
    pass


class Reader():
    def __init__(self, article, readSetting):
        self.article = article
        self.title = article.getTitle()
        self.paragraphs = article.getParagraphs()

        self.readSetting = readSetting

    def read(self):
        self.readTitle()
        for paragraph in self.paragraphs:
            if len(paragraph.getContent()) != 0:
                self.readParagraph(paragraph)
                command = str(input("Please press enter to continue"))

    def readTitle(self):
        print(self.title.getEnTitle())
        command = str(input("Please press enter to continue"))
        if command != 'n':
            print(self.title.getCnTitle())

    def readParagraph(self, paragraph):
        print("Content:\t" + paragraph.getContent())
        command = str(input("Please press enter to continue"))
        if command != 'n':
            if paragraph.getInterpretion() != None:
                print("interpretation:\t" + paragraph.getInterpretion())

    def drawReaderMenu(self):
        print("Please press enter to continue")


class Article():
    def __init__(self, title):
        self.title = title
        self.paragraphs = []

    def addParagraph(self, paragraph):
        self.paragraphs.append(paragraph)

    def getTitle(self):
        return self.title

    def getParagraphs(self):
        return self.paragraphs


class Title():

    def __init__(self, id, enTitle, cnTitle):
        self.id = id
        self.enTitle = enTitle
        self.cnTitle = cnTitle

    def getId(self):
        return self.id

    def getEnTitle(self):
        return self.enTitle

    def getCnTitle(self):
        return self.cnTitle


class Paragraph():
    def __init__(self, id, content, interpretion):
        self.id = id
        self.content = content
        self.interpretion = interpretion

    def getContent(self):
        return self.content

    def getInterpretion(self):
        return self.interpretion


class Spider():
    def flatArticle(self, articelId):
        api = ShanbayApi()
        (title, other) = api.getArticleDetail(articelId)
        article = Article(title)
        paragraphDics = api.readArticleFromXml(other)
        for paragraphId in paragraphDics.keys():
            interpretation = api.getInterpretation(paragraphId)
            article.addParagraph(Paragraph(paragraphId, paragraphDics[paragraphId], interpretation))
        return article


def start():
    def clearShell():
        os.system('cls' if os.name == 'nt' else 'clear')

    def drawArticleList():
        # clearShell()
        titles = ShanbayApi().printArticlesOverview()
        for title in titles:
            print(title.id, '\t', title.enTitle, '\t', title.cnTitle)

    def mainMenu():
        spider = Spider()
        readSetting = ReadSetting()

        while True:
            drawArticleList()
            articleId = str(input('Please enter the article id that you want to read:\n'))
            article = spider.flatArticle(articleId)
            reader = Reader(article, readSetting)
            reader.read()
            clearShell()

    mainMenu()


start()
