#!/usr/bin/env python
# encoding=utf-8

"""
抓取知乎所有话题列表
"""


from xtls.basecrawler import BaseCrawler
from xtls.util import BeautifulSoup
from xtls.logger import get_logger
from xtls.codehelper import forever
from json import dumps, loads
from config import *
from pymongo import MongoClient

logger = get_logger(__file__)
BASE_TOPICS = [u'253', u'833', u'99', u'69', u'113', u'304', u'13908', u'570', u'1761', u'988', u'388', u'285', u'686', u'444', u'1537', u'3324', u'2955', u'4196', u'395', u'75', u'68', u'215', u'1027', u'445', u'112', u'237', u'1740', u'1538', u'2143', u'4217', u'2253', u'8437', u'19800']
ZHIHU_URL = 'http://www.zhihu.com'
TOPIC_URL = 'http://www.zhihu.com/node/TopicsPlazzaListV2'
MONGO = MongoClient(MONGO_HOST, MONGO_PORT)


class TopicCrawler(BaseCrawler):

    def __init__(self, topic_id):
        super(TopicCrawler, self).__init__(topic_id=topic_id)

    def _run(self, offset):
        result = []
        data = {
            'method': 'next',
            'params': '{"topic_id":%s,"offset":%s,"hash_id":""}' % (self.topic_id, offset),
            '_xsrf': '690bc39a80e99e2089d2e0cb0f504e0d'
        }
        resp = self.post(TOPIC_URL, data)
        msgs = loads(resp)['msg']
        for msg in msgs:
            soup = BeautifulSoup(msg)
            a = soup.find('a')
            link = a['href'].strip()
            result.append({
                '_id': link[link.rfind('/')+1:],
                'link': ZHIHU_URL + link,
                'topic': a.getText().strip(),
                'icon': a.find('img')['src'].strip(),
            })
        return result

    @classmethod
    def save(cls, data):
        MONGO[DB][TOPIC_COLL].update_one({'_id': data['_id']}, {'$set': data}, upsert=True)

    def run(self):
        for pos in forever(0):
            offset = pos * 20
            logger.info('now %s-%s' % (self.topic_id, offset))
            data = self._run(offset)
            for item in data:
                self.save(item)
            if len(data) != 20:
                break


def main():
    for topic in BASE_TOPICS:
        TopicCrawler(topic).run()


if __name__ == '__main__':
    main()
