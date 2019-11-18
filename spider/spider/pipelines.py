# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from spider.spiders.lj_region import LjRegionSpider
from spider.settings import MONGODB_URL
class RegionPipeline(object):
    num=0
    def open_spider(self,spider):
        if isinstance(spider,LjRegionSpider):
            self.client=MongoClient(MONGODB_URL)
            self.collection=self.client['lj']['region']
    def process_item(self, item, spider):
        if isinstance(spider,LjRegionSpider):
            count=self.collection.count_documents({'_id':item['region_url']})
            if count ==0:
                dic=dict(item)
                dic['_id']=item['region_url']
                self.collection.insert_one(dic)
                self.num=self.num+1
                print("插入新的代理,{}".format(self.num))
            else:
                print("已经存在的代理：{}".format(item))
        return item
    def close_spider(self,spider):
        if isinstance(spider,LjRegionSpider):
            self.client.close()
from spider.spiders.lj_zufang import LjZufangSpider
class ZufangPipeline(object):
    num=0
    def open_spider(self,spider):
        if isinstance(spider,LjZufangSpider):
            self.client=MongoClient(MONGODB_URL)
            self.collection=self.client['lj']['house']
    def process_item(self, item, spider):
        if isinstance(spider,LjZufangSpider):
            count=self.collection.count_documents({'_id':item['house_code']})
            if count ==0:
                dic=dict(item)
                dic['_id']=item['house_code']
                self.collection.insert_one(dic)
                self.num=self.num+1
                print("插入新的代理,{}".format(self.num))
            else:
                print("已经存在的代理：{}".format(item))
        return item
    def close_spider(self,spider):
        if isinstance(spider,LjZufangSpider):
            self.client.close()
