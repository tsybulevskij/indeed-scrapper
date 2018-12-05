# -*- coding: utf-8 -*-
from scrapy.utils.serialize import ScrapyJSONEncoder

from tasks import insert_item

encoder = ScrapyJSONEncoder()


class JobScrapyPipeline(object):
    def __init__(self):
        self.items = []

    @classmethod
    def from_crawled(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline)

    def process_item(self, item, spider):
        self.items.append(item._values)
        if len(self.items) >= 2000:
            insert_item.delay(item=self.items)
        return item

    def close_spider(self, spider):
        if self.items:
            insert_item.delay(item=self.items)

