import arxiv
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import MAX_PAPERS_TO_FETCH, ARXIV_RETRY_ATTEMPTS

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(ARXIV_RETRY_ATTEMPTS), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def fetch_arxiv_papers(query: str, max_results: int = MAX_PAPERS_TO_FETCH) -> list[dict]:
    """
    Fetches papers from ArXiv based on a query.
    Includes retry logic using tenacity for resilience against intermittent API timeouts.
    """
    logger.info(f"Fetching up to {max_results} papers from ArXiv for query: '{query}'")
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = []
    # arxiv package generators can sometimes timeout during iteration
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary.replace('\n', ' '),
            "link": result.entry_id,
            "published": result.published.strftime("%Y-%m-%d")
        })
        
    logger.info(f"Successfully fetched {len(papers)} papers from ArXiv.")
    return papers
