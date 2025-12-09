"""
workflow.py
Creates and assembles the agriculture content workflow.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

def create_researcher_agent():
    """Create the research agent."""
    return Agent(
        name="researcher",
        model=Gemini(model="gemini-2.0-flash-exp"),
        description="Research specialist for gathering agricultural AI information",
        instruction="""You are a research specialist. Use Google Search to find current, accurate information about AI applications in agriculture. Focus on finding reliable sources, statistics, case studies, and recent developments. Return well-structured research notes with citations.""",
        tools=[google_search],
    )

def create_writer_agent():
    """Create the content writer agent."""
    return Agent(
        name="writer",
        model=Gemini(model="gemini-2.0-flash-exp"),
        description="Professional content writer for LinkedIn posts",
        instruction="""You are a professional content writer specializing in LinkedIn posts. Create engaging, professional content about AI in agriculture. Format for LinkedIn with proper spacing, emojis, and hashtags. Keep it concise (300-500 words), engaging, and suitable for professionals in tech and agriculture.""",
    )

def create_verifier_agent():
    """Create the fact-checking agent."""
    return Agent(
        name="verifier",
        model=Gemini(model="gemini-2.0-flash-exp"),
        description="Fact-checker for agricultural AI content",
        instruction="""You are a fact-checking specialist. Verify the accuracy of information about AI in agriculture. Cross-reference with known facts and research. Identify any claims that need verification or clarification. Return a verification report with any corrections needed.""",
        tools=[google_search],
    )

def create_master_agent():
    """
    Create a master agent that orchestrates the entire workflow.
    This agent coordinates between researcher, writer, and verifier.
    """
    return Agent(
        name="agriculture_content_master",
        model=Gemini(model="gemini-2.0-flash-exp"),
        description="Master agent for agriculture content pipeline",
        instruction="""You are the master coordinator for creating agriculture AI LinkedIn posts.

Your workflow:
1. RESEARCH PHASE: Search for current information about the given agriculture/AI topic. Find statistics, case studies, and recent developments.
2. WRITING PHASE: Create a professional LinkedIn post based on the research. Include:
   - Engaging hook
   - Key insights
   - Practical applications
   - Future outlook
   - Relevant hashtags
3. VERIFICATION PHASE: Fact-check the post for accuracy. Verify claims, statistics, and information.
4. ITERATION: If corrections are needed, rewrite the post to address them.

Execute this complete workflow for the given topic. Return only the final LinkedIn post.""",
        tools=[google_search],
    )

def create_content_pipeline():
    """
    Create and return the complete content pipeline.
    For simplicity, we'll use a single master agent that handles the entire workflow.
    """
    return create_master_agent()
