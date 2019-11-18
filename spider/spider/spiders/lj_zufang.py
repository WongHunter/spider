# -*- coding: utf-8 -*-
import scrapy
import pickle
from scrapy_redis.spiders import RedisSpider
from spider.items import HouseItem

class LjZufangSpider(RedisSpider):
    name = 'lj_zufang'
    allowed_domains = ['lianjia.com']
    redis_key='lj_house:region'
    num=0
    def make_request_from_data(self, data):
        """
        根据redis中读取的分类信息的二进制数据，构建请求
        :param data:分类信息的二进制数据
        :return:根据小分类URL，构建请求对象
        """
        region=pickle.loads(data)
        return scrapy.Request(region['region_url'],callback=self.parse,cookies=region['cookies'],meta={'region':region})
    def parse(self, response):
        region=response.meta['region']
        if response.url==region['region_url']:
            pg_num=response.xpath('//*[@class="content__pg"]/@data-totalpage').extract_first()
            if pg_num!=None and int(pg_num)!=0:
                for i in range(1,int(pg_num)+1):
                    pg_url=region['region_url']+'pg{}'.format(i)
                    region['pg_url']=pg_url
                    yield scrapy.Request(pg_url,callback=self.parse_houses,cookies=region['cookies'],meta={'region':region})
                    # yield scrapy.Request(pg_url,callback=self.parse_houses,cookies=region['cookies'],meta=region)

            else:
                print(222,pg_num,region)
        else:
            print(111,region,response.url)
    def parse_houses(self, response):
        meta=response.meta['region']
        if response.url==meta['pg_url']:
            region={}
            region['province_name']=meta['province_name']
            region['city_name']=meta['city_name']
            region['city_url']=meta['city_url']
            region['area_name']=meta['area_name']
            region['area_url']=meta['area_url']
            region['region_name']=meta['region_name']
            region['region_url']=meta['region_url']
            houses=response.xpath('//*[@class="content__list--item"]')
            for house in houses:
                item=HouseItem()
                #房源区域
                item['house_region']=region
                #房源编号
                item['house_code']=house.xpath('./@data-house_code').extract_first()
                #房源标题
                item['house_title']=house.xpath('./div/p[1]/a/text()').extract_first().strip()
                #租赁方式
                if '合租' in item['house_title']:
                    item['house_lease']='合租'
                else:
                    item['house_lease']='整租'
                #房源价格
                item['house_price']=house.xpath('.//div/span/em/text()').extract_first().split('-')
                item['house_min_price']=int(item['house_price'][0])
                item['house_max_price']=int(item['house_price'][-1])
                #房源图url
                item['house_img_url']=house.xpath('./a/img/@src').extract_first()
                if '.jpg'not in item['house_img_url']:
                    item['house_img_url']=house.xpath('./a/img/@data-src').extract_first()
                #房源地址
                item['house_address']=house.xpath('.//*[@class="content__list--item--des"]/a[3]/text()').extract_first()
                # house_temp=house.xpath('./div/*[@class="content__list--item--des"]/text()').extract()
                # for i in house_temp:
                #     i=i.strip()
                #     if i!='-'and i!='':
                #         if '㎡'in i:
                #             #房源面积
                #             item['house_area']=i
                #         if '室'in i:
                #             #房源布局，类型
                #             item['house_layout']=i
                #房源标签
                item['house_tags']=house.xpath('./div/p[@class="content__list--item--bottom oneline"]/i/text()').extract()
                #房源url
                item['house_url']=house.xpath('./div/p/a/@href').extract_first()
                if item['house_url'].find('apartment')==-1:
                    item['house_url']='https://m.lianjia.com/chuzu/'+item['house_region']['city_url'][8:-12]
                    item['house_url']=item['house_url']+'/zufang/{}.html'.format(item['house_code'])
                    yield scrapy.Request(item['house_url'],callback=self.parse_house_data,meta={'item':item})
                else:
                    #公寓url
                    item['apartment_url']=item['house_region']['city_url']+item['house_url']
                    item['house_url']='https://m.lianjia.com/chuzu/'+item['house_region']['city_url'][8:-12]
                    item['house_url']=item['house_url']+'/apartment/layout/{}.html'.format(item['house_code'])
                    yield scrapy.Request(item['house_url'],callback=self.parse_house_data,meta={'item':item})
            # 所有信息，正则
            # temp=response.xpath('//*[@class="wrapper"]/script[2]').extract_first()
        else:
            print(333,meta,response.url)
    def parse_house_data(self, response):
        item=response.meta['item']
        if response.url==item['house_url']:
            #房源信息
            item['house_infos']={}
            #户型
            layout_k=response.xpath('//*[@class="box content__detail--info"]/ul/li[2]/span[1]/text()').extract_first()
            layout_v=response.xpath('//*[@class="box content__detail--info"]/ul/li[2]/span[2]/text()').extract_first()
            if layout_k and layout_v:
                item['house_infos'][layout_k]=layout_v.split()[0]
            #小区
            info_k=response.xpath('//*[@class="resblock"]/span/text()').extract_first()
            info_v=response.xpath('//*[@class="resblock"]/a/text()').extract_first()
            if layout_k and layout_v:
                item['house_infos'][info_k[:-1]]=info_v.split()[0]
            #租期，看房
            info_k=response.xpath('//*[@class="rent-short"]/span/text()').extract()
            info_v=response.xpath('//*[@class="rent-short"]/label/text()').extract()
            for i in range(len(info_k)):
                item['house_infos'][info_k[i][:-1]]=info_v[i]
            #房源信息
            info_k=response.xpath('//*[@class="page-house-info-list"]/li/label/text()').extract()
            info_v=response.xpath('//*[@class="page-house-info-list"]/li/span/text()').extract()
            for i in range(len(info_k)):
                item['house_infos'][info_k[i][:-1]]=info_v[i]
            #房源标签
            house_tags=response.xpath('//*[@class="content__item__tag--wrapper"]/i/text()').extract()
            if house_tags:
                item['house_tags'].extend(house_tags)
                item['house_tags']=set(item['house_tags'])
                item['house_tags']=list(item['house_tags'])
            #房源图url
            if '.jpg' not in item['house_img_url']:
                item['house_img_url']=response.xpath('//*[@data-el="lazy-img"]/@src').extract_first()
            if '.jpg' not in item['house_img_url']:
                item['house_img_url']=response.xpath('//*[@data-el="lazy-img"]/@data-src').extract_first()
                print(item['house_img_url'])
            #房源交通
            temp=response.xpath('//*[@class="box page-map-list"]/li')
            if temp:
                item['house_traffics']=[]
            for i in range(len(temp)):
                stations=temp[i].xpath('./text()').extract()
                house_traffics=','.join(temp[i].xpath('./i/text()').extract())
                house_traffic=house_traffics+'   '+temp[i].xpath('./span/text()').extract_first()
                for station in stations:
                    station=station.split()
                    if len(station)!=0:
                        item['house_traffics'].append(station[0]+'   '+house_traffic)
            #房源年租费
            temp=response.xpath('//*[@class="house-cost-box cost-box-year  bb-1px"]//*[@class="title"]/text()').extract()
            postfix=response.xpath('//*[@class="house-cost-box cost-box-year  bb-1px"]//*[@class="sub_title"]/text()').extract()
            if temp:
                item['house_annual_rent']={}
                cost_k=[]
            for i in temp:
                i=i.split()
                if len(i)!=0:
                   cost_k.append(i[0])
            cost_v=response.xpath('//*[@class="house-cost-box cost-box-year  bb-1px"]/table/tbody/tr/td/text()').extract()
            for i in range(len(cost_v)):
                cost_v[i]=cost_v[i].split()[0]
                if i!=0:
                    cost_k[i]=cost_k[i]+ postfix[i-1]
                item['house_annual_rent'][cost_k[i]]=cost_v[i]
            #房源月租费
            temp=response.xpath('//*[@class="house-cost-box cost-box-month cost-box-hide cost-box-all-hide"]//*[@class="title"]/text()').extract()
            postfix=response.xpath('//*[@class="house-cost-box cost-box-month cost-box-hide cost-box-all-hide"]//*[@class="sub_title"]/text()').extract()
            if temp:
                item['house_month_rent']={}
                cost_k=[]
            for i in temp:
                i=i.split()
                if len(i)!=0:
                   cost_k.append(i[0])
            cost_v=response.xpath('//*[@class="house-cost-box cost-box-month cost-box-hide cost-box-all-hide"]/table/tbody/tr/td/text()').extract()
            for i in range(len(cost_v)):
                cost_v[i]=cost_v[i].split()[0]
                if i!=0:
                    cost_k[i]=cost_k[i]+ postfix[i-1]
                item['house_month_rent'][cost_k[i]]=cost_v[i]

            #房源描述
            temp=response.xpath('//*[@class="box detail"]/a/text()').extract()
            if temp:
                item['house_describes']=''
            for i in temp:
                i=i.split()
                if len(i)!=0:
                        item['house_describes']=item['house_describes']+' '.join(i)
            #配套设施
            temp=response.xpath('//*[@class="oneline"]/text()').extract()
            house_facilities=[]
            for i in temp:
               i=i.split()
               if len(i)!=0:
                   house_facilities.append(i[0])
            if house_facilities:
                item['house_facilities']=house_facilities
            #房源地图
            item['house_map']=response.xpath('//*[@class="map--container"]/@href').extract_first()
            if item['house_map']:
                item['house_map']='https://m.lianjia.com/'+item['house_map']
            #入住
            info_k='入住'
            info_v=response.xpath('//*[@class="layout__status "]/text()').extract_first()
            if info_v:
                item['house_infos'][info_k]=info_v.split()[0]
            #房源地址 公寓地址 公寓名
            house_address=response.xpath('//*[@class="flat_detail--link"]/p/text()').extract()
            if house_address:
                item['house_address']=house_address[1]+' —— '+house_address[0]
            # try:
            #     if item['house_month_rent']:
            #         print(1111)
            # except:
            #     a=item.get('house_annual_rent')
            #     print(a)
            if ['house_infos']:
                if '㎡' in item['house_infos']['面积']:
                    item['house_infos']['面积']=item['house_infos']['面积'][:-1].split('-')
                    item['house_infos']['最小面积']=item['house_infos']['面积'][0]
                    item['house_infos']['最大面积']=item['house_infos']['面积'][-1]
                else:
                    item['house_infos']['面积']=item['house_infos']['面积'][:-2].split('-')
                    item['house_infos']['最小面积']=item['house_infos']['面积'][0]
                    item['house_infos']['最大面积']=item['house_infos']['面积'][-1]
            self.num=self.num+1
            print(self.num)
            if item.get('apartment_url'):
                yield scrapy.Request(item['apartment_url'],callback=self.parse_apartment_data,meta={'item':item})
            else:
                if item['house_infos']:
                    if item['house_infos']['维护']:
                        url=item['house_region']['city_url']+'/zufang/{}.html'.format(item['house_code'])
                        yield scrapy.Request(url,callback=self.parse_house_date,meta={'item':item})
        else:
            print(444,response.url,item)
    def parse_apartment_data(self, response):
        item=response.meta['item']
        if response.url==item['apartment_url']:
            #公寓描述
            temp=response.xpath('//*[@class="flat__info--description threeline"]/text()').extract()
            if temp:
                item['apartment_describes']=''
            for i in temp:
                i=i.split()
                if len(i)!=0:
                        item['apartment_describes']=item['apartment_describes']+' '.join(i)
            #公寓配套设施
            apartment_facilities=response.xpath('//*[@id="facility"]/ul/li/text()').extract()
            if apartment_facilities:
                item['apartment_facilities']=apartment_facilities
            yield item
            # #房源地址
            # house_address=response.xpath('//*[@class="flat__info--subtitle online"]/text()').extract_first()
            # apartment_name=response.xpath('//*[@class="flat__info--title online"]/text()').extract_first()
            # if house_address and apartment_name:
            #     item['house_address']=house_address.strip()+apartment_name
            # elif house_address and apartment_name == None:
            #     item['house_address']=house_address.strip()+response.xpath('//*[@class="aside_neme"]/text()').extract_first()
            # elif house_address==None and apartment_name :
            #     item['house_address']=apartment_name
            # else:
            #     item['house_address']=response.xpath('//*[@class="aside_neme"]/text()').extract_first()
        else:
            print(555,response.url,item)
    def parse_house_date(self, response):
        item=response.meta['item']
        if response.url==item['house_region']['city_url']+'/zufang/{}.html'.format(item['house_code']):
            item['house_infos']['维护']=response.xpath('//div[@class="content__subtitle"]/text()').extract()
            item['house_infos']['维护']=item['house_infos']['维护'][1].split()[0]
            item['house_infos']['维护']=item['house_infos']['维护'][7:]
            yield item
        else:
            print(666,response.url,item)
