from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    State dictionary representing the agent's memory during the LangGraph execution.
    """
    topic: str
    papers: List[Dict[str, Any]]  # List to store raw paper metadata from ArXiv
    summary: List[Dict[str, Any]] # List to store parsed summaries from Gemini
    report: str                   # The final synthesized markdown report
