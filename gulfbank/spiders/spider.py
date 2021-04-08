import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import GgulfbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class GgulfbankSpider(scrapy.Spider):
	name = 'gulfbank'
	start_urls = ['https://www.gulfbank.com/about-us/recent-news']

	def parse(self, response):
		post_links = response.xpath('//div[@class="blog-more"]//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		try:
			date = response.xpath('//div[@class="blog-meta"]/p/strong/text()').get().split('on ')[1]
		except IndexError:
			date = response.xpath('//div[@class="blog-meta"]/p/strong/text()').get()
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="blog-post"]//text()[not (ancestor::div[@class="blog-meta"] or ancestor::div[@class="blog-tags"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=GgulfbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
