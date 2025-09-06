import requests
import os

from app.models.post import PostContentRequest

def search_web(post_content: str):
    """Search for web links related to the post content using Google Custom Search API."""
    api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")
    
    # Check if API credentials are available
    if not api_key or not search_engine_id:
        print(f"Warning: Google Custom Search API credentials not found. API Key: {bool(api_key)}, Search Engine ID: {bool(search_engine_id)}")
        return []
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": post_content,
        "key": api_key,
        "cx": search_engine_id,
        "num": 5,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            search_results = response.json().get("items", [])
            return search_results
        else:
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Error searching for links: {str(e)}")
        return []
    except Exception as e:
        print(f"Unexpected error during search: {str(e)}")
        return []


def get_links(post_data: PostContentRequest):
    """Get links from search results for post verification."""
    search_results = search_web(post_data.content)
    
    if not search_results:
        return []
    
    links = []
    for item in search_results:
        if item.get("link"):
            links.append(item["link"])
    
    return links