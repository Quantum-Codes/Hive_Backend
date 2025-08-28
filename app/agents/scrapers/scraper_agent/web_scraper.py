# TODO: Implement web scraping logic here
# This file will contain web scraping functionality for post verification
# Examples: scrape news sites, fact-checking sources, extract relevant information
#
# ASSIGNED TO: Ankit Sinha
# TASK: Implement web scraping functionality for post verification
# - Scrape news sites and fact-checking sources
# - Extract relevant information from various content types
# - Handle different sources and content formats
# - Implement error handling and rate limiting
# - Integration with RAG pipeline for data processing

import bs4, sys, os
import requests, datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from models.scraper import ScraperResult

class WebScraper:

    def __init__(self):
        pass

    def webscrape(self, url):
        # detect base url
        if url.startswith("https://www.indiatoday.in/"):
            return self._indiatoday_webscrape(url)
        elif url.startswith("https://www.livemint.com/"):
            return self._livemint_webscrape(url)
        else:
            raise ValueError("Site not allowed")


    def _indiatoday_webscrape(self, url):
        
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Failed to retrieve content")

        soup = bs4.BeautifulSoup(response.content, "html5lib") # to fix broken tags returned by indiatoday
        # body -> div#__next -> div#main -> div.temp__container -> div.temp__layout -> div.content__section  -> main
        div_main = soup.body.find("div", id="__next").find("div", id="main")
        div_temp_container = div_main.find("div", class_="temp__container")
        content_section = div_temp_container.find("div", class_="temp__layout").find("div", class_="content__section")
        main_tag = content_section.find("main").find("div", class_ = "lhs__section")

        title = main_tag.find("h1").text.strip().strip("\"")
        summary = main_tag.find("div", class_ = "Story_w__100__e1YfC").find("div", class_ = "wapper__kicker").find("h2").text.strip().strip("\"")

        content_body = main_tag.find("div", class_ = "widgetgap")

        time_posted = content_body.find("div", class_ = "Story_story__byline__7MVK3").find("div", class_ = "Story_profile__details__wyZj7")
        time_posted = time_posted.find("div", class_ = "Story_stryupdates__wdMz_").find("span", class_ = "strydate").text.strip().replace("UPDATED: ", "")
        # May 20, 2025 16:22 IST - format
        time_posted = datetime.datetime.strptime(time_posted, "%b %d, %Y %H:%M IST") # assumtion always IST since indian website

        articles = []
        paras = content_body.find("div", class_ = "story-with-main-sec").find("div", class_ = "description")      
        paras = paras.find_all("p")
        for p in paras:
            articles.append(p.text.strip())
        

        return ScraperResult(
            source=url,
            title=title,
            article_summary=summary,
            date_published=time_posted,
            content=articles
        )

    def _livemint_webscrape(self, url):

        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Failed to retrieve content")

        soup = bs4.BeautifulSoup(response.content, "html5lib")
        # div#__next -> div.containerNew -> div.midSec -> div.storyPage_storyBox__9iWpG
        content_body = soup.body.find("div", id="__next").find("div", class_="clearfix")
        content_body = content_body.find("div", class_="midSec")
        content_body = content_body.find("div", class_="storyPage_storyBox__9iWpG")

        title = content_body.find("h1", id="article-0").text.strip().strip("\"")
        summary = content_body.find("h2", class_="storyPage_summary__K7jOt").text.strip().strip("\"")

        time_posted = content_body.find("div", class_ = "storyPage_authorSocial__z7nHm").find("div", class_ = "storyPage_authorInfo__Dj3b4").find("div", class_ = "storyPage_authorDesc__cKKWd").find("div", class_ = "storyPage_date__iM8Kb").find("span").text.strip().strip("\"")
        # 27 Aug 2025, 12:09 AM IST - format
        time_posted = datetime.datetime.strptime(time_posted, "%d %b %Y, %I:%M %p IST")

        articles = []
        paras = content_body.find("div", class_ = "storyPage_storyContent__3xuFc").find_all("div", class_ = "storyParagraph")

        for item in paras:
            articles.append(item.find("p").text.strip().strip("\""))
        

        return ScraperResult(
            source=url,
            title=title,
            article_summary=summary,
            date_published=time_posted,
            content=articles
        )

