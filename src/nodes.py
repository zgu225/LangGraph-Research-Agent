import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from src.state import AgentState
from src.tools import fetch_arxiv_papers
from src.config import GEMINI_MODEL_NAME, REPORT_LANGUAGE

logger = logging.getLogger(__name__)

# Pydantic models for structured output to ensure reliability
class PaperSummary(BaseModel):
    key_contributions: str = Field(description="The main problem solved and key contributions of the paper")
    methodology: str = Field(description="Brief explanation of the proposed method or approach")
    limitations: str = Field(description="Any limitations or future work mentioned in the paper")

def get_llm():
    """Initializes and returns the Gemini LLM."""
    return ChatGoogleGenerativeAI(model=GEMINI_MODEL_NAME, temperature=0.2)

def search_node(state: AgentState) -> Dict[str, Any]:
    """Node: Searches ArXiv for relevant papers."""
    topic = state.get("topic", "")
    logger.info(f"--- Node: search_node --- | Topic: {topic}")
    
    papers = fetch_arxiv_papers(topic)
    return {"papers": papers}

def summarize_node(state: AgentState) -> Dict[str, Any]:
    """Node: Synthesizes core insights from each fetched paper serially."""
    logger.info("--- Node: summarize_node ---")
    papers = state.get("papers", [])
    summaries = []
    
    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=PaperSummary)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI researcher analyzing an academic preprint. Extract the key contributions, methodology, and limitations from the abstract and title. Return EXCLUSIVELY a JSON object conforming to the requested schema. Respond in {language}."),
        ("user", "Title: {title}\nAuthors: {authors}\nAbstract: {abstract}")
    ])
    
    chain = prompt | llm | parser
    
    # Serial Execution: We summarize in a loop.
    # Future Work / Interview talking point: This can be highly optimized via 
    # asyncio.gather or ThreadPoolExecutor for concurrent requests.
    for idx, paper in enumerate(papers):
        logger.info(f"Summarizing paper {idx+1}/{len(papers)}: {paper['title']}")
        try:
            result = chain.invoke({
                "title": paper["title"],
                "authors": ", ".join(paper["authors"]),
                "abstract": paper["abstract"],
                "language": REPORT_LANGUAGE
            })
            
            # Combine the original paper metadata with the LLM's structured insights
            summary_info = {
                "title": paper["title"],
                "link": paper["link"],
                "published": paper["published"],
                "authors": paper["authors"],
                **result
            }
            summaries.append(summary_info)
        except Exception as e:
            logger.error(f"Error summarizing paper '{paper['title']}': {e}")
            
    return {"summary": summaries}

def report_node(state: AgentState) -> Dict[str, Any]:
    """Node: Compiles all summaries into a final, highly readable markdown report."""
    logger.info("--- Node: report_node ---")
    topic = state.get("topic", "")
    summaries = state.get("summary", [])
    
    llm = get_llm()
    
    prompt_sys = (
        "You are an expert technical writer and AI researcher. Synthesize the provided academic paper "
        "summaries into a comprehensive, highly readable Research Report about '{topic}'. "
        "The report MUST be written entirely in {language}.\n\n"
        "Format the report beautifully using Markdown. Include:\n"
        "1. **Title**: An engaging title\n"
        "2. **Introduction**: A brief overview of the research topic\n"
        "3. **Thematic Sections**: Group similar papers together and synthesize their contributions, architectures, or findings rather than just listing them one by one.\n"
        "4. **Conclusion**: A summary of current trends and open challenges.\n"
        "5. **References**: A bulleted list of all papers referenced, including authors, publication date, and ArXiv link."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_sys),
        ("user", "Here are the extracted insights from relevant papers:\n\n{summaries_text}")
    ])
    
    # Format the extracted summaries into a string for the report generator
    summaries_text = ""
    for idx, s in enumerate(summaries):
        summaries_text += f"[{idx+1}] {s['title']} ({s['published']})\n"
        summaries_text += f"- Authors: {', '.join(s['authors'])}\n"
        summaries_text += f"- Link: {s['link']}\n"
        summaries_text += f"- Key Contributions: {s.get('key_contributions', '')}\n"
        summaries_text += f"- Methodology: {s.get('methodology', '')}\n"
        summaries_text += f"- Limitations & Future Work: {s.get('limitations', '')}\n\n"
        
    chain = prompt | llm
    
    logger.info("Generating Final Report... This may take a moment.")
    response = chain.invoke({
        "topic": topic,
        "language": REPORT_LANGUAGE,
        "summaries_text": summaries_text
    })
    
    return {"report": response.content}
