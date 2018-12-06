# -*- coding: utf-8 -*-
import scrapy

import os
import csv
import glob
import MySQLdb


class JobsSpider(scrapy.Spider):
    name = 'jobs'
    allowed_domains = ['sfbay.craigslist.org']
    start_urls = ['https://sfbay.craigslist.org/search/sof?']

    def parse(self, response):
        items = response.xpath('//*[@id="sortable-results"]/ul/li')            
        for item in items:
            link = item.xpath('./a/@href').extract_first()
            title = item.xpath('./p/a/text()').extract_first()
            place = item.xpath('./p/span[@class = "result-meta"]/span[@class = "result-hood"]/text()').extract_first()            
            
            yield scrapy.Request(response.urljoin(link),callback=self.parse_detail)
            # meta = {'Link':link,
            #         'Title':title,
            #         'Place':place})
            
        nextpageurl = response.xpath('//*[@id="searchform"]/div[5]/div[3]/span[2]/a[3]/@href').extract_first()
        if nextpageurl:
            yield scrapy.Request(response.urljoin(nextpageurl),callback=self.parse)
        
    def parse_detail(self, response):
        date = response.xpath('//*[@id="display-date"]/time[@class = "date timeago"]/@datetime').extract_first()
        link = response.meta['Link']
        title = response.meta['Title']
        place = response.meta['Place']
        # group = [title,place,link,date]
        
        yield{
                'Title':title,
                'Place':place,
                'Link':link,
                'Date':date,
                }
        
        
    def close(self,reason):
        csv_file = max(glob.iglob('*.csv'),key = os.path.getctime)
        
        mydb = MySQLdb.connect(host = 'localhost',user = 'root',db = 'sampleDB')
        cursor = mydb.cursor()
        csv_data = csv.reader(file(csv_file))
        row_count = 0
        
        for row in csv_data:
            if row_count != 0:
                cursor.execute('insert into sampleTB(title,place,link,date) VALUES (%s,%s,%s,%s)',row)
            print row_count
            row_count += 1
        
        mydb.commit()
        cursor.close()
        
            