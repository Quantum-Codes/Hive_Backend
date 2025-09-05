import requests
import os

from app.models.post import PostContentRequest

def search_web(post_content: str):
    api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": post_content,
        "key": api_key,
        "cx": search_engine_id,
        "num": 5,
    }
    
    print(f"Searching the links related to the post content: {post_content}")
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    if response.status_code == 200:
        search_results = response.json().get("items", [])
        return search_results 
    """
    search_results = [
        {
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet"),
        }
        for item in search_results
    ]
    """
    
    
def get_links(post_data: PostContentRequest):
    links = search_web(post_data.content)
    return [link["link"] for link in links]