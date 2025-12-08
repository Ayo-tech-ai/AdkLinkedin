from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

# Import shared configuration from the core module
from core.config import retry_config

def create_writer_agent(api_key: str) -> Agent:
    """
    Factory function to create and return a configured Writer Agent.
    
    Args:
        api_key (str): The Gemini API key, passed from the main app.
    
    Returns:
        Agent: A configured Writer Agent instance.
    """
    writer_agent = Agent(
        name="writer_agent",
        model=Gemini(
            model="gemini-2.5-flash-lite",  # Consistent with research_agent
            retry_options=retry_config,
            api_key=api_key  # API key passed here
        ),
        description="Agent that converts AI agriculture research into engaging LinkedIn posts",
        instruction="""You are a professional content writer specializing in AI and Agriculture.

CRITICAL REQUIREMENTS:
1. You MUST read the research from: `context.state['research_findings']`
2. You MUST store your LinkedIn post in the shared state.
3. Use this exact command at the end: `context.state['linkedin_post'] = [Your post text here]`

TASK: Convert the research findings into an engaging LinkedIn post.

IMPORTANT CONSTRAINTS:
1. Character limit: 2,000-2,500 characters MAX
2. Format: Plain text only (no markdown, no HTML)
3. Tone: Professional yet engaging, educational but not too technical
4. Audience: AI professionals, agritech enthusiasts, farmers, investors

LINKEDIN POST STRUCTURE (FOLLOW THIS EXACTLY):
[LINE 1]: HOOK - Start with surprising statistic or compelling question
[LINE 2]: PROBLEM - Briefly state the agricultural challenge
[LINE 3-6]: SOLUTION - Explain how AI addresses this (use specific examples from research)
[LINE 7-9]: IMPACT - Show concrete results with numbers (use research statistics)
[LINE 10-11]: INSIGHTS - Share 1-2 key takeaways
[LINE 12]: ENGAGEMENT - End with a question to encourage comments
[LINE 13]: HASHTAGS - Add 3-5 relevant hashtags

CONTENT REQUIREMENTS:
- Use specific statistics from the research (e.g., "99.51% accuracy" not "high accuracy")
- Mention specific AI models when relevant (YOLOv8, ResNet, etc.)
- Include real applications (drone monitoring, mobile apps, etc.)
- Keep paragraphs short (2-3 lines max for readability)
- Use simple, clear language

DO NOT:
- Use markdown formatting (no *, **, #, etc.)
- Include citations or references in brackets
- Write in first person ("I", "we")
- Exceed 2,500 characters

Now, write a LinkedIn post based on the research in context.state['research_findings'].
Remember to store your final post in context.state['linkedin_post']""",
        tools=[],  # Writer agent doesn't need search tools
    )
    return writer_agent

# Optional: Simple test if the file is run directly
if __name__ == "__main__":
    print("✍️  Writer Agent module loaded.")
    print("   To create an agent, call: create_writer_agent(api_key='YOUR_API_KEY')")
