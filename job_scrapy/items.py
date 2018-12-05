import scrapy


class JobScrapyItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    city = scrapy.Field()
    zip = scrapy.Field()
    description = scrapy.Field()
    text_html = scrapy.Field()
    posted_date = scrapy.Field()
    stars = scrapy.Field()
    original_url = scrapy.Field()
    post_url = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    period = scrapy.Field()
    filter_salary = scrapy.Field()
    sponsored = scrapy.Field()
    start_url = scrapy.Field()
    page_order = scrapy.Field()
