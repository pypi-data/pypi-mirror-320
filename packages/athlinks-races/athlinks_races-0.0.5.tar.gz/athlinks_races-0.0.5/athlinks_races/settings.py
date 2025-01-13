"""
 Scrapy settings for scraper project

 For simplicity, this file contains only settings considered important or
 commonly used. You can find more settings consulting the documentation:

     https://docs.scrapy.org/en/latest/topics/settings.html
     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
"""

BOT_NAME = 'athlinks_races'

SPIDER_MODULES = ['athlinks_races.spiders']
NEWSPIDER_MODULE = 'athlinks_races.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
