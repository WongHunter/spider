# -*- coding: utf-8 -*-
import scrapy
from spider.items import RegionItem

class LjRegionSpider(scrapy.Spider):
    name = 'lj_region'
    allowed_domains = ['lianjia.com']
    start_urls = ['https://www.lianjia.com/city']
    num=0
    def parse(self, response):
        divs=response.xpath('//*[@class="city_list_ul"]/li/div[@class="city_list"]/div')
        for div in divs:
            item={}
            item['province_name']=div.xpath('./div/text()').extract_first()
            cities=div.xpath('./ul/li/a')
            for city in cities:
                item['city_name']=city.xpath('./text()').extract_first()
                item['city_url']=city.xpath('./@href').extract_first()
                item['city_url']=item['city_url'][:-1]
                yield scrapy.Request(item['city_url'],callback=self.parse_cookies,meta=item)
    def parse_cookies(self, response):
        item=response.meta
        city_id=response.xpath('//*[@id="findHouse"]/@daty-id').extract_first()
        if city_id:
            item['cookies']={'select_city': city_id}
            index_url=response.url+'/zufang'
            yield scrapy.Request(index_url,cookies=item['cookies'],callback=self.parse_city,meta=item)
    def parse_city(self,response):
        item=response.meta
        num=response.xpath('//*[@class="content__title--hl"]/text()').extract_first()
        if num!='0':
            areas=response.xpath('//*[@data-target="area"]/li[position()>1]/a')
            for area in areas:
                item['area_name']=area.xpath('./text()').extract_first()
                item['area_url']=area.xpath('./@href').extract_first()
                item['area_url']=item['city_url']+item['area_url']
                yield scrapy.Request(item['area_url'],cookies=item['cookies'],callback=self.parse_area,meta=item)
    def parse_area(self,response):
        item=response.meta
        num=response.xpath('//*[@class="content__title--hl"]/text()').extract_first()
        if num!='0':
            regions=response.xpath('//*[@data-type="bizcircle"][position()>1]/a')
            for region in regions:
                item['region_name']=region.xpath('./text()').extract_first()
                item['region_url']=region.xpath('./@href').extract_first()
                item['region_url']=item['city_url']+item['region_url']
                yield scrapy.Request(item['region_url'],callback=self.parse_data,cookies=item['cookies'],meta=item)
    def parse_data(self,response):
        meta=response.meta
        num=response.xpath('//*[@class="content__title--hl"]/text()').extract_first()
        if num!='0':
            item=RegionItem()
            item['province_name']=meta['province_name']
            item['city_name']=meta['city_name']
            item['city_url']=meta['city_url']
            item['area_name']=meta['area_name']
            item['area_url']=meta['area_url']
            item['region_name']=meta['region_name']
            item['region_url']=meta['region_url']
            item['cookies']=meta['cookies']
            # temp=['防城港','保定','泰安','江阴','海门']
            # if item['city_name'] in temp:
            #     print(item['city_name'],item['area_name'],item['region_name'],item['region_url'],num)
            self.num=self.num+1
            print(self.num)
            yield item
