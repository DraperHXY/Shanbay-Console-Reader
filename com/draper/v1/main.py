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
        res = self.rs.get(url, params=params, headers=self.headers, verify=False)
        dicData = json.loads(res.text)
        return dicData['data']['objects']

    def printArticlesOverview(self):
        articelsInfos = self.getArticlesOverview()

        for line in articelsInfos:
            print(line['id'], '\t', warning_start + line['title_en'] + warning_end)
            print(line['title_cn'])
            print()

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
        res = self.rs.get(url, headers=self.headers, verify=False)
        assert res.status_code == 200
        dicData = json.loads(res.text)
        return dicData['data']['content']

    def readArticleFromXml(self, xmlStr):
        root = ET.XML(xmlStr)
        for paraNode in root.iter('para'):
            print(paraNode.get('id'))
            for sentNode in paraNode.iter('sent'):
                print('' + '\t' + warning_start + sentNode.text + warning_end)

    def getInterceptor(self, id):
        url = self.baseApi + '/news/notes/?para_id=' + id + '&ipp=3&page=1'
        print(url)
        res = self.rs.get(url, headers=self.headers, verify=False)
        print(res)
        return json.loads(res.text)['data']['objects'][0]['content']


def main():
    api = ShanbayApi()

    """1. 获取文档目录"""
    for line in api.getArticlesOverview():
        api.getArticleDetail(line['id'])

    """2. 通过文章目录获取 id"""
    api.printArticlesOverview()

    """3. 通过 id 来获取文章的详细内容"""
    articleId = str(input('\n输入你想看文章内容的id:\t')).lower()
    xmlStr = api.getArticleDetail(articleId)

    # file = open('temp.xml', 'w')
    # file.write(xmlStr)

    api.readArticleFromXml(xmlStr)
    # print(xmlStr)

    paraId = str(input('\n输入你想看段落翻译的id:\t'))
    interceptor = api.getInterceptor(paraId)
    print(interceptor)


main()


# print(ShanbayApi().getInterceptor('A167450P918918'))


class FakeUserConfig:
    pass


class FakeBrowserConfig:
    def getHeaders(self):
        pass
