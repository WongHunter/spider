# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
class RegionItem(scrapy.Item):
    province_name=scrapy.Field()
    city_name=scrapy.Field()
    city_url=scrapy.Field()
    area_name=scrapy.Field()
    area_url=scrapy.Field()
    region_name=scrapy.Field()
    region_url=scrapy.Field()
    cookies=scrapy.Field()
class HouseItem(scrapy.Item):
    #公寓url
    apartment_url=scrapy.Field()
    #公寓信息
    apartment_describes=scrapy.Field()
    #配套设施
    apartment_facilities=scrapy.Field()

    #房源url
    house_url=scrapy.Field()
    #房源区域
    house_region=scrapy.Field()
    #房源编号
    house_code=scrapy.Field()
    #房源标题
    house_title=scrapy.Field()
    #房源价格
    house_price=scrapy.Field()
    house_min_price=scrapy.Field()
    house_max_price=scrapy.Field()
    #租赁方式
    house_lease=scrapy.Field()
    #房源面积
    house_area=scrapy.Field()
    #房源布局，类型
    house_layout=scrapy.Field()
    #房源标签
    house_tags=scrapy.Field()
    #房源图url
    house_img_url=scrapy.Field()
    #房源地址
    house_address=scrapy.Field()

    #房源信息
    house_infos=scrapy.Field()
    #房源交通
    house_traffics=scrapy.Field()
    #房源年租费
    house_annual_rent=scrapy.Field()
    #房源月租费
    house_month_rent=scrapy.Field()
    #房源描述
    house_describes=scrapy.Field()
    #配套设施
    house_facilities=scrapy.Field()
    #房源地图
    house_map=scrapy.Field()
