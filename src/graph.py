from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes import search_node, summarize_node, report_node

def build_graph():
    """
    Builds and compiles the LangGraph StateGraph connecting the agent's nodes.
    """
    # Initialize the graph with the defined AgentState
    workflow = StateGraph(AgentState)
    
    # Add functional nodes
    workflow.add_node("search", search_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("report", report_node)
    
    # Define the execution flow (Edges)
    workflow.add_edge(START, "search")
    workflow.add_edge("search", "summarize")
    workflow.add_edge("summarize", "report")
    workflow.add_edge("report", END)
    
    # Compile the graph into an executable application
    app = workflow.compile()
    return app
