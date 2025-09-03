# TODO: Implement verification service logic here
# This file will contain business logic for post verification
# Examples: verify post content, classify posts, handle verification results
#
# ASSIGNED TO: Team collaboration (Dhruv Pokhriyal + Ankit Sinha + Karthik)
# TASK: Implement business logic for post verification
# - Coordinate between scraping and RAG pipeline
# - Handle verification results and classification
# - Manage verification status and metadata
# - Integration with post service
# - Verification result storage and retrieval

from app.agents.scrapers.scraper_agent.web_scraper import WebScraper
from app.agents.search_agent.search_agent import get_links, search_web
from app.models.rag import RagRequest
from app.models.schemas import PostContentRequest, PostVerificationRequest
from agents.rag_agent.rag_agent import VerificationRAGPipeline
    

pipeline = VerificationRAGPipeline()
web_scrapper = WebScraper()


def get_context(post_data: PostContentRequest):
    links = get_links(post_data)
    context = [web_scrapper.webscrape(link) for link in links]
    return context


def verify_post(post_data: PostContentRequest):
    """Verify a post using the RAG pipeline.

    Args:
        post_data (PostContentRequest): The post data to verify.

    Returns:
        _type_: _description_
    """
    context = get_context(post_data)
    request = RagRequest(
        post_id=post_data.pid,
        post_content=post_data.content,
        context=context
    )
    response = pipeline.verify(request, top_k=4)
    return response

