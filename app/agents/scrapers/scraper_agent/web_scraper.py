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

import bs4
import requests


ALLOWED_SITES = [
    "https://www.indiatoday.in/",
]

def webscrape(url):
    # check whitelist

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Failed to retrieve content")

    # print(response.content)
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    # body -> div#__next -> div#main -> div.temp__container -> div.temp__layout -> div.content__section  -> main
    div_main = soup.body.find("div", id="__next").find("div", id="main")
    div_temp_container = div_main.find("div", class_="temp__container")
    content_section = div_temp_container.find("div", class_="temp__layout")
    content_section = content_section.find("div", class_="content__section")
    main_tag = content_section.find("main").find("div", class_ = "lhs__section")

    title = main_tag.find("h1").text.strip().strip("\"")
    summary = main_tag.find("div", class_ = "Story_w__100__e1YfC").find("div", class_ = "wapper__kicker").find("h2").text.strip().strip("\"")


    print(title, summary, sep="\n\n")





if __name__ == "__main__":
    webscrape("https://www.indiatoday.in/technology/news/story/google-io-2025-starts-tonight-here-is-how-to-watch-and-details-on-possible-announcements-2727614-2025-05-20")