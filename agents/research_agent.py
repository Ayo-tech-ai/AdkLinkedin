from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

# Import shared configuration from the core module
from core.config import retry_config

def create_research_agent(api_key: str) -> Agent:
    """
    Factory function to create and return a configured Research Agent.
    
    Args:
        api_key (str): The Gemini API key, passed from the main app.
    
    Returns:
        Agent: A configured Research Agent instance.
    """
    research_agent = Agent(
        name="research_agent",
        model=Gemini(
            model="gemini-2.5-flash-lite",  # Using 2.0-flash as per our working setup
            retry_options=retry_config,
            api_key=api_key  # Critical: The API key is passed here
        ),
        description="Agent that researches AI in agriculture topics using Google Search",
        instruction="""You are a research specialist in AI and Agriculture. Your task is to find recent, credible information about AI applications in agriculture.

CRITICAL REQUIREMENT:
- You MUST store your final research findings in the shared state.
- Use this exact command at the end: `context.state['research_findings'] = [Your research text here]`

When given a topic:
1. Search for the latest developments (last 1-2 years)
2. Focus on credible sources: academic papers, reputable tech blogs, agricultural organizations
3. Look for specific examples, case studies, statistics, and practical applications
4. Find 5-10 key insights about the topic
5. Organize findings clearly with facts, statistics, and examples

RESEARCH FORMAT (Same as before):
MAIN TOPIC: [Topic Name]

KEY FINDINGS:
1. [Finding 1 with statistic]
2. [Finding 2 with example]

CURRENT APPLICATIONS:
- [Application 1]
- [Application 2]

STATISTICS AND IMPACT:
- [Stat 1 with source]
- [Stat 2 with source]

LIMITATIONS AND CHALLENGES:
- [Challenge 1]
- [Challenge 2]

FUTURE TRENDS:
- [Trend 1]
- [Trend 2]

Remember: Store your research in context.state['research_findings']""",
        tools=[google_search],
    )
    return research_agent

# Optional: Simple test if the file is run directly
if __name__ == "__main__":
    # This is just for testing the agent creation logic
    print("🔍 Research Agent module loaded.")
    print("   To create an agent, call: create_research_agent(api_key='YOUR_API_KEY')")
