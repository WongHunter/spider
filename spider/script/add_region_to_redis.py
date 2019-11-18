#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：albert time:2019/11/6 0006
from pymongo import MongoClient
from redis import StrictRedis
import pickle
from spider.settings import MONGODB_URL,REDIS_URL
from spider.spiders.lj_zufang import LjZufangSpider
def add_region_to_redis():
    mongo=MongoClient(MONGODB_URL)
    redis=StrictRedis.from_url(REDIS_URL)
    collection=mongo['lj']['region']
    cursor=collection.find()
    num=0
    for region in cursor:
        num=num+1
        print(num)
        data=pickle.dumps(region)
        redis.lpush(LjZufangSpider.redis_key,data)
    mongo.close()
if __name__ == '__main__':
    add_region_to_redis()
