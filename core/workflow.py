from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types
import asyncio

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

def create_agriculture_workflow(researcher, writer, verifier):
    """
    Assemble the complete workflow with the three agents.
    This function defines how agents interact.
    """
    # Define the workflow logic
    @researcher.on_response
    async def research_to_writer(ctx, response):
        """Pass research results to writer."""
        research_summary = response.text
        
        # Prepare query for writer
        writer_query = f"""Based on this research, create a professional LinkedIn post:

Research Summary:
{research_summary}

Create a LinkedIn post with:
1. Engaging hook
2. Key insights from research
3. Practical applications
4. Future outlook
5. Relevant hashtags"""
        
        # Call writer agent
        writer_response = await writer.respond(ctx, writer_query)
        return writer_response

    @writer.on_response
    async def writer_to_verifier(ctx, response):
        """Pass draft to verifier."""
        draft_content = response.text
        
        # Prepare query for verifier
        verifier_query = f"""Verify the accuracy of this LinkedIn post draft:

Draft:
{draft_content}

Check for:
1. Factual accuracy
2. Supported claims
3. Up-to-date information
4. Any exaggerations or unsupported statements"""
        
        # Call verifier agent
        verifier_response = await verifier.respond(ctx, verifier_query)
        return verifier_response

    @verifier.on_response
    async def verifier_feedback(ctx, response):
        """Handle verification feedback."""
        verification_report = response.text
        
        # Check if verification passed
        if "accurate" in verification_report.lower() or "correct" in verification_report.lower():
            return response  # Return final response
        
        # If corrections needed, rewrite
        rewrite_query = f"""Rewrite the LinkedIn post incorporating these corrections:

Corrections Needed:
{verification_report}

Please revise the post to address all verification issues."""
        
        rewrite_response = await writer.respond(ctx, rewrite_query)
        return rewrite_response

    return researcher  # Return the entry point agent

def create_content_pipeline():
    """
    Create and return the complete content pipeline using InMemoryRunner.
    This is the main entry point for the pipeline.
    """
    # Create agents
    researcher = create_researcher_agent()
    writer = create_writer_agent()
    verifier = create_verifier_agent()
    
    # Assemble workflow
    workflow = create_agriculture_workflow(researcher, writer, verifier)
    
    return workflow
