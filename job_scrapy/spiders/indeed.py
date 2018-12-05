import re
import csv
from datetime import datetime, timedelta
from urllib.parse import urlparse

import scrapy

from ..items import JobScrapyItem


class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_urls = ['indeed.com']

    def start_requests(self):
        try:
            with open('start_urls.csv', 'r') as csv_file:  # path to file with urls
                urls = csv.reader(csv_file)
                start_urls = [
                    ''.join(url)
                    for url in urls
                ]
                order_number_on_page = 0
                for url in start_urls:
                    result = urlparse(url)
                    if result.scheme and result.netloc:
                        yield scrapy.Request(
                            url,
                            dont_filter=True,
                            meta={
                                'start_url': url,
                                'order_number_on_page': order_number_on_page
                            },
                            callback=self.parse
                        )
        except FileNotFoundError:
            self.log('File not found')

    def parse(self, response):
        url_posts = response.xpath(
            '//td[@id="resultsCol"]//h2[@class="jobtitle"]/a/@href'
        ).extract()
        sponsored_posts = self.parse_sponsored(response)
        filter_salary = self.parse_filter_salary(response)
        page_order = self.parse_order(response)
        start_url = response.meta.get('start_url')

        for url in sponsored_posts:
            yield scrapy.Request(
                'https://www.indeed.com' + url,
                callback=self.parse_original_url,
                meta={
                    'filter_salary': filter_salary,
                    'sponsored': 'sponsored'
                },
                dont_filter=True
            )

        for url in url_posts:
            yield scrapy.Request(
                'https://www.indeed.com' + url,
                callback=self.parse_original_url,
                dont_filter=True,
                meta={
                    'filter_salary': filter_salary,
                    'start_url': start_url,
                    'page_order': page_order,
                    'sponsored': None
                }
            )

        next_url = response.xpath(
            '//span[contains(text(), "Next")]/../../@href'
        ).extract_first()

        if next_url is not None:
            next_page = 'https://www.indeed.com' + next_url
            yield response.follow(
                next_page,
                callback=self.parse,
                dont_filter=True,
                meta={
                    'start_url': start_url
                }
            )

        salary_filter_urls = response.xpath(
            '//div[@id="SALARY_rbo"]//a/@href'
        ).extract()

        if salary_filter_urls:
            for filter_url in salary_filter_urls:
                yield response.follow(
                    filter_url,
                    callback=self.parse,
                    dont_filter=True,
                    meta={
                        'start_url': start_url
                    }
                )

    def parse_original_url(self, response):
        item = JobScrapyItem()

        item['title'] = self.parse_title(response)
        item['company'] = self.parse_company(response)
        item['city'] = self.parse_city(response)
        item['zip'] = self.parse_zip(response)
        item['description'] = self.parse_description(response)
        item['posted_date'] = self.parse_posted_date(response)
        item['stars'] = self.parse_ratings(response)
        item['post_url'] = response.url
        item['min_salary'] = self.parse_min_salary(response)
        item['max_salary'] = self.parse_max_salary(response)
        item['text_html'] = self.parse_text_html(response)
        item['period'] = self.parse_period(response)
        item['filter_salary'] = response.meta.get('filter_salary')
        item['sponsored'] = response.meta.get('sponsored')
        item['start_url'] = response.meta.get('start_url')
        item['page_order'] = response.meta.get('page_order')

        original_url = response.xpath(
            '//span[@id="originalJobLinkContainer"]/a/@href'
        ).extract_first()
        if original_url:
            yield scrapy.Request(
                original_url,
                meta={'item': item},
                callback=self.parse_post,
                errback=self.handle_error,
                dont_filter=True
            )

    def handle_error(self, failure):
        self.log('Request failed: %s. Reason: response timeout.' % failure.request)
        item = failure.request.meta.get('item')
        item['original_url'] = None

        yield item

    def parse_post(self, response):
        item = response.meta.get('item')
        item['original_url'] = response.url

        yield item

    def parse_title(self, response):
        return response.xpath(
            '//h3[contains(@class, "JobInfoHeader-title")]/text()'
        ).extract_first()

    def parse_company(self, response):
        return response.xpath(
            '//div[contains(@class, "InlineCompanyRating")]//text()'
        ).extract_first()

    def parse_city(self, response):
        data = response.xpath(
            '//div[contains(@class, "InlineCompanyRating")]//text()'
        ).extract()
        if data:
            return re.sub(r'\d+', '', data[-1]).strip()

    def parse_zip(self, response):
        data = response.xpath(
            '//div[contains(@class, "InlineCompanyRating")]//text()'
        ).extract()
        if data:
            zip = ''.join(re.findall(r'\d+', data[-1]))
            if zip != '':
                return zip

    def parse_description(self, response):
        data = response.xpath(
            '//div[contains(@class, "JobComponent-description")]//text()'
        ).extract()
        if data:
            return ''.join([text.strip() for text in data])

    def parse_posted_date(self, response):
        data = response.xpath(
            '//div[contains(@class, "JobMetadataFooter")]/text()'
        ).extract_first()
        if data:
            days_ago = ''.join(re.findall(r'\d+', data))
            posted_date = datetime.now() - timedelta(days=int(days_ago))
            return posted_date.strftime('%Y-%m-%d')

    def parse_ratings(self, response):
        data = response.xpath(
            '//div[contains(@class, "InlineCompanyRating")]'
            '//a[contains(@class, "Ratings-starsCountWrapper")]/@aria-label'
        ).extract()
        if data:
            return ''.join([stars[0:-9] for stars in data])

    def parse_min_salary(self, response):
        data = response.xpath(
            '//div[contains(@class, "JobMetadataHeader-item")]/text()'
        ).extract()
        if data:
            salary = ''.join(data)
            salary = salary.replace(',', '.')
            float_salary = re.search(r'\d+.\d+', salary)
            int_salary = re.search(r'\d+', salary)
            if float_salary:
                return float_salary.group()
            elif int_salary:
                return int_salary.group()

    def parse_max_salary(self, response):
        data = response.xpath(
            '//div[contains(@class, "JobMetadataHeader-item")]/text()'
        ).extract()
        if data:
            salary = ''.join(data)
            salary = salary.replace(',', '.')
            float_salary = re.findall(r'\d+.\d+', salary)
            int_salary = re.findall(r'\d+', salary)
            if float_salary:
                return float_salary[-1]
            elif int_salary:
                return int_salary[-1]

    def parse_text_html(self, response):
        return response.xpath(
            '//div[contains(@class, "JobComponent-description")]'
        ).extract()

    def parse_period(self, response):
        data = response.xpath(
            '//div[contains(@class, "JobMetadataHeader-item")]/text()'
        ).extract_first()
        if data:
            period = data.split()
            if 'year' in period:
                return re.search(r'\byear\b', data).group()
            elif 'month' in period:
                return re.search(r'\bmonth\b', data).group()
            elif 'day' in period:
                return re.search(r'\bday\b', data).group()
            elif 'hour' in period:
                return re.search(r'\bhour\b', data).group()

    def parse_filter_salary(self, response):
        data = response.xpath(
            '//input[@name="q"]/@value'
        ).extract_first()
        salary = data.replace(',', '.')
        float_salary = re.search(r'\d+.\d+', salary)
        if float_salary:
            return str(float_salary.group())

    def parse_sponsored(self, response):
        sponsored = response.xpath(
            '//span[contains(@class, "sponsoredGray")]/ancestor::div[@class="sjCapt"]/ancestor::div/a[@class="jobtitle turnstileLink"]/@href'
        ).extract()
        return sponsored

    def parse_order(self, response):
        data = response.xpath('//div[@class="pagination"]/b/text()').extract_first()
        if data:
            return int(data)
