#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：albert time:2019/11/11 0011
from pymongo import MongoClient
import pandas as pd
import math
from spider.settings import MONGODB_URL
from spider.items import HouseItem,RegionItem
def get_region():
    mongo=MongoClient(MONGODB_URL)
    collection=mongo['lj']['region']
    count=collection.estimated_document_count()
    num=math.ceil(count/10)
    limit=10
    for i in range(0,num):
        skip=limit*i
        cursor=collection.find().skip(skip).limit(limit)
        for item in cursor:
            item.pop('_id')
            region=RegionItem(**item)
            yield region
    mongo.close()
def get_house(city_name):
    mongo=MongoClient(MONGODB_URL)
    collection=mongo['lj']['house']
    count=collection.estimated_document_count()
    sort=[("house_min_price", 1),("house_infos.最小面积", -1)]
    query = { "house_region.city_name": city_name }
    num=math.ceil(count/10)
    limit=10
    for i in range(0,num):
        skip=limit*i
        cursor=collection.find(query).sort(sort).skip(skip).limit(limit)
        for item in cursor:
            item.pop('_id')
            house=HouseItem(**item)
            yield house
    mongo.close()
if __name__ == '__main__':
    files=set()
    for region in get_region():
        files.add(region['city_name'])
    files=list(files)
    for file in files:
        data=[]
        for house in get_house(file):
            item={}
            item.update(house['house_infos'])
            item.update(house['house_region'])
            del house['house_infos']
            del house['house_region']
            item.update(house)
            data.append(item)
        if len(data)!=0:
            file='../data/{}.xlsx'.format(file)
            df=pd.DataFrame(data)
            excel=df.set_index('house_code')
            excel.to_excel(file)

