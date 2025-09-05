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
from newspaper import Article

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
        elif url.startswith("https://www.ndtv.com/"):
            return self._ndtv_webscrape(url)
        else:
            return self._generic_webscrape(url)


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


    def _ndtv_webscrape(self, url):

        headers = {
            "Sec-CH-UA": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            # more descriptive
            print(f"Failed to retrieve: {response.status_code}")
            print(response.text)
            raise ValueError("Failed to retrieve content")

        soup = bs4.BeautifulSoup(response.content, "html5lib")
        # div.vjl-cnt -> div.vjl-cntr -> div.vjl-row -> div.vjl-Mid-1 -> div.vjl-row -> div.vjl-Mid-2 -> div.stp-wr -> div.sp-hd -> div.sp-cn -> 
        content_body = soup.body.find("div", class_="vjl-cnt").find("div", class_="vjl-cntr").find("div", class_="vjl-row").find("div", class_="vjl-Mid-1")

        title = content_body.find("h1", class_="sp-ttl").text.strip().strip("\"").strip()
        summary = content_body.find("h2", class_="sp-descp").text.strip().strip("\"").strip()
        time_posted = content_body.find("nav", class_ = "pst-by").find("ul", class_ = "pst-by_ul").find_all("li")[2].find("span").text.strip().strip("\"").strip()
        # format - Sep 02, 2025 16:11 pm IST
        time_posted = datetime.datetime.strptime(time_posted, "%b %d, %Y %H:%M %p IST")

        paras = content_body.find("div", class_ = "sp_txt").find("div", class_ = "Art-exp_cn").find("div", class_ = "Art-exp_wr").find_all("p")

        articles = []
        for item in paras:
            articles.append(item.text.strip().strip("\""))
        
        return ScraperResult(
            source=url,
            title=title,
            article_summary=summary,
            date_published=time_posted,
            content=articles
        )
    
    def _generic_webscrape(self, url):
        """
        A generic fallback scraper that uses the newspaper library to extract content.
        """
        try:
            article = Article(url)
            article.download()
            article.parse()

            # Extract content
            title = article.title
            content = article.text
            summary = article.summary
            date_published = article.publish_date or datetime.datetime.now()

            return ScraperResult(
                source=url,
                title=title,
                article_summary=summary,
                date_published=date_published,
                content=content.split('\n')
            )
        except Exception as e:
            print(f"Failed to process {url} with newspaper3k: {e}")
            # Fallback to the previous generic scraper if newspaper fails
            return self._old_generic_webscrape(url)
        

    def _old_generic_webscrape(self, url):
        """
        A generic fallback scraper that extracts all meaningful text from a URL.
        It tries to remove common non-content elements like ads, scripts, and navigation.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.RequestException as e:
            print(f"Failed to retrieve content from {url}: {e}")
            raise ValueError(f"Failed to retrieve content from {url}")

        soup = bs4.BeautifulSoup(response.content, "html5lib")

        # Remove non-content tags
        for tag in soup(["script", "style", "footer", "header", "iframe", "noscript"]):
            tag.decompose()

        # Remove elements that are likely ads
        for ad_element in soup.find_all(
            lambda tag: "ad" in tag.get("id", "").lower()
            or "ad" in " ".join(tag.get("class", [])).lower()
            or "google" in tag.get("id", "").lower()
            or "google" in " ".join(tag.get("class", [])).lower()
        ):
            ad_element.decompose()

        # Extract text from the body
        body_text = soup.body.get_text(separator="\n", strip=True)
        
        # Split text into a list of non-empty lines
        articles = [line for line in body_text.split("\n") if line]

        title = soup.title.string.strip() if soup.title else "No title found"

        return ScraperResult(
            source=url,
            title=title,
            article_summary=None,
            date_published=None,  # Use current time as a fallback
            content=articles,
        )

    
if __name__ == "__main__":
    ws = WebScraper()
    url = "https://livemint.com/technology/tech-news/google-i-o-2025-kicks-off-from-today-what-to-expect-and-how-to-watch-livestream-11747721444594.html"
    result = ws.webscrape(url)
    print(result.title)
    print(result.date_published)
    print(result.article_summary)
    print(result.content[:5])  # Print first 5 paragraphs
