import os
import argparse
import datetime
import logging
from dotenv import load_dotenv

from src.graph import build_graph
from src.config import REPORTS_DIR

# Setup simple console logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    # Load environment variables (such as GEMINI_API_KEY)
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY is not set. Please copy .env.example to .env and add your valid key.")
        return

    # Ensure the outputs directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("\n" + "="*60)
    print("Welcome to the LangGraph ArXiv Research Agent!")
    print("="*60)
    
    while True:
        # Use interactive input instead of argparse
        topic = input("\nPlease enter the research topic you want to query (or type 'exit' or 'q' to quit): ").strip()
        
        if not topic:
            logger.error("Topic cannot be empty. Please try again.")
            continue
            
        if topic.lower() in ['exit', 'q', 'quit']:
            print("\nExiting the Agent. Goodbye!")
            break
        
        logger.info(f"Starting ArXiv Research Agent...")
        logger.info(f"Target Topic: '{topic}'")
        
        # Build the LangGraph workflow application
        app = build_graph()
        
        # Set the initial state for the graph
        initial_state = {"topic": topic}
        
        # Execute the workflow
        try:
            logger.info("Triggering LangGraph workflow... Please wait while papers are analyzed.")
            final_state = app.invoke(initial_state)
            report_content = final_state.get("report")
            
            if report_content:
                # Generate a clean filename based on topic and timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_topic = topic.replace(" ", "_").replace("/", "-").lower()
                filename = f"{safe_topic[:30]}_{timestamp}.md"
                filepath = os.path.join(REPORTS_DIR, filename)
                
                # Save the markdown report to disk
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(report_content)
                    
                logger.info("Successfully generated bilingual markdown report.")
                logger.info(f"Report Output Saved to: {filepath}\n")
            else:
                logger.warning("Agent execution finished, but no report was found in the final state.\n")
                
        except Exception as e:
            logger.error(f"Failed to run agent successfully: {e}\n", exc_info=True)

if __name__ == "__main__":
    main()
