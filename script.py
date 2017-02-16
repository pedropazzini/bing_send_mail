import re
import scrapy

class bing(scrapy.Spider):
    name = "Bing"
    core_link = 'http://www.bing.com/'
    start_urls = [core_link]

    def parse(self,response):
        link_img = re.search("az(.*?)jpg",response.body).group(0).replace('\\','')
        self.full_link_img = self.core_link + link_img

        link = response.xpath('//a[@id="sh_cp"]/@href').extract()[0]
        new_link = self.core_link + link
        yield scrapy.Request(new_link,callback=self.parse_info)
        #yield {'img_link':self.full_link_img,'extra': data}
        #return self.full_link_img,self.title,self.description

    def parse_info(self,response):

        try:
            self.title = response.xpath('//h2[@class=""]/text()')[1].extract()
        except:
            self.title = 'NONE'

        try:
            self.description = response.xpath('//div[@class="b_vPanel"]/div')[-2].extract()
        except:
            self.description = 'NONE'

        yield{'title':self.title,'description':self.description,'img_link':self.full_link_img}
