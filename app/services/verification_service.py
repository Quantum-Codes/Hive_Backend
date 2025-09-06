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

from app.agents.scraper_agent.web_scraper import WebScraper
from app.agents.search_agent.search_agent import get_links, search_web
from app.models.rag import RagRequest
from app.models.scraper import ScraperResult
from app.models.post import PostContentRequest, PostVerificationRequest
from app.agents.rag_agent.rag_agent import VerificationRAGPipeline
from app.core.supabase import get_supabase_client

pipeline = VerificationRAGPipeline()
web_scraper = WebScraper()


def get_context(post_data: PostContentRequest):
    """Get context for post verification by scraping relevant links.
    
    Args:
        post_data (PostContentRequest): The post data to get context for
        
    Returns:
        List[ScraperResult]: List of scraped content results
    """
    try:
        links = get_links(post_data)
        
        if not links:
            return []
        
        context = []
        for link in links:
            try:
                result = web_scraper.webscrape(link)
                if result:  # Only add non-None results
                    context.append(result)
            except Exception as e:
                print(f"Failed to scrape link {link} for post {post_data.pid}: {str(e)}")
                continue
        
        return context
    except Exception as e:
        print(f"Error getting context for post {post_data.pid}: {str(e)}")
        return []


def scraperresult_to_context_string(result: ScraperResult) -> str:
    """Convert a ScraperResult to a formatted context string.
    
    Args:
        result (ScraperResult): The scraped result to convert
        
    Returns:
        str: Formatted context string
    """
    if not result:
        return ""
    
    try:
        title = result.title or "No title"
        summary = result.article_summary or "No summary"
        source = result.source or "Unknown source"
        content = result.content or []
        
        # Create a more concise context string
        context_parts = []
        
        # Add title and summary (most important)
        if title != "No title":
            context_parts.append(f"Title: {title}")
        if summary != "No summary":
            context_parts.append(f"Summary: {summary}")
        
        # Add source
        if source != "Unknown source":
            context_parts.append(f"Source: {source}")
        
        # Add limited content (first few paragraphs)
        if content:
            # Limit content to first 3 paragraphs or 500 characters
            content_text = "\n".join(content[:3])  # First 3 paragraphs
            if len(content_text) > 500:
                content_text = content_text[:500] + "..."
            context_parts.append(f"Content: {content_text}")
        
        return "\n".join(context_parts)
    except Exception as e:
        print(f"Error converting scraper result to context string: {str(e)}")
        return f"Error processing content: {str(e)}"



def verify_post(post_data: PostContentRequest):
    """Verify a post using the RAG pipeline.

    Args:
        post_data (PostContentRequest): The post data to verify.

    Returns:
        dict: Verification response with status, confidence, and metadata
    """
    try:
        supabase = get_supabase_client()
        
        # Get context for verification
        context = get_context(post_data)
        context_strings = [scraperresult_to_context_string(result) for result in context]
        
        # Limit context size to avoid API payload limits
        max_context_length = 8000  # Limit total context to ~8KB
        total_length = sum(len(ctx) for ctx in context_strings)
        if total_length > max_context_length:
            print(f"Context too large ({total_length} chars), truncating to {max_context_length} chars")
            truncated_contexts = []
            current_length = 0
            for ctx in context_strings:
                if current_length + len(ctx) <= max_context_length:
                    truncated_contexts.append(ctx)
                    current_length += len(ctx)
                else:
                    # Add partial context if there's space
                    remaining = max_context_length - current_length
                    if remaining > 100:  # Only add if there's meaningful space
                        truncated_contexts.append(ctx[:remaining] + "...")
                    break
            context_strings = truncated_contexts
        
        # If no context found, add a general knowledge context for well-known facts
        if not context_strings or all(not ctx.strip() for ctx in context_strings):
            context_strings = [
                "This is a general knowledge verification context. "
                "Consider well-known facts, historical events, scientific principles, "
                "and commonly accepted information when evaluating the claim."
            ]

        request = RagRequest(
            post_id=post_data.pid,
            post_content=post_data.content,
            context=context_strings
        )
        
        response = pipeline.verify(request, top_k=4)
        
        # Get the verification status from the response (already a string)
        verification_status = response.get('status', 'unverified')
        
        # Validate that the status is one of the expected values
        from app.models.rag import RagResponse
        valid_statuses = [status.value for status in RagResponse]
        if verification_status not in valid_statuses:
            verification_status = 'unverified'

        # Update the database with the string value
        update_result = supabase.table('posts').update({
            "verification_status": verification_status,
        }).eq("pid", post_data.pid).execute()
        
        if not update_result.data:
            print(f"Warning: Failed to update verification status for post {post_data.pid}")
        
        return response
        
    except Exception as e:
        print(f"Error during verification for post {post_data.pid}: {str(e)}")
        
        # Update database with error status
        try:
            supabase = get_supabase_client()
            supabase.table('posts').update({
                "verification_status": "unverified",
            }).eq("pid", post_data.pid).execute()
        except Exception as db_error:
            print(f"Failed to update error status in database: {str(db_error)}")
        
        # Return error response
        return {
            "status": "unverified",
            "confidence": 0.0,
            "answer": "Verification failed due to an error",
            "supporting_context": [],
            "rationale": f"Error during verification: {str(e)}",
            "metadata": {
                "post_id": post_data.pid,
                "error": True
            },
        }