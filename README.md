install各种相关的依赖库

第一种：用pip导出项目中的dependency：

$ pip freeze > requirements.txt

第二种：先安装pip install pipreqs

然后命令行执行 pipreqs ./生成requirements.txt

然后通过以下命令来安装dependency:

$ pip install -r requirements.txt

项目结构：

spider

	spider
	
		spiders
		
			lJ_region.py
			
			lj_zufang.py
			
		items.py
		
		middlewares.py
		
		pipelines.py
		
		settings.py
		
	script
	
		add_zufang_to_excel.py
		
		add_region_to_redis.py
		
	data
	
		城市名.xlsx
架构：python3.7 mongodb redis

使用了scrapy框架

先执行lJ_region爬虫，把城市信息，URL信息保存到mongdb

执行add_region_to_redis.py脚本，把url保存在redis,

先执行lJ_zufang爬虫，从redis读取俩爬取租房信息并保存到mongdb

最后执行add_zufang_to_excel.py脚本，形成excel形式的数据报表
