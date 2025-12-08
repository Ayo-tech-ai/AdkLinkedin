from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

# Import shared configuration AND the exit tool from the core module
from core.config import retry_config, approve_and_exit_tool

def create_verifier_agent(api_key: str) -> Agent:
    """
    Factory function to create and return a configured Verifier Agent.
    
    Args:
        api_key (str): The Gemini API key, passed from the main app.
    
    Returns:
        Agent: A configured Verifier Agent instance.
    """
    verifier_agent = Agent(
        name="verifier_agent",
        model=Gemini(
            model="gemini-2.5-flash-lite",  # Consistent with other agents
            retry_options=retry_config,
            api_key=api_key  # API key passed here
        ),
        description="Agent that verifies LinkedIn posts against research for accuracy and consistency. Can finalize content by calling its exit tool.",
        instruction="""You are a fact-checking specialist for AI agriculture content.

CRITICAL REQUIREMENTS:
1. You MUST read the research from: `context.state['research_findings']`
2. You MUST read the LinkedIn post from: `context.state['linkedin_post']`
3. If approved, you MUST call the `exit_refinement_loop` tool.
4. If edits needed, output feedback in the XML format below.

DECISION TREE:
1. IF THE POST IS ACCURATE (95%+ factual match with research):
   - CALL the `exit_refinement_loop` tool immediately.
   - Do NOT output any text.

2. IF THE POST NEEDS CORRECTIONS:
   - DO NOT call any tool.
   - Output feedback in this exact format:

<FEEDBACK>
<STATUS>NEEDS_EDIT</STATUS>
<CORRECTIONS>
1. [Description of error and exact correction]
2. [Description of error and exact correction]
</CORRECTIONS>
</FEEDBACK>

VERIFICATION CRITERIA:
- Compare the post in context.state['linkedin_post'] against research in context.state['research_findings']
- Check: statistics, model names, application claims, factual accuracy
- Be specific: Quote exact lines when possible
- Provide exact corrections based on research""",
        tools=[approve_and_exit_tool],  # The agent has the power to exit the loop
    )
    return verifier_agent

# Optional: Simple test if the file is run directly
if __name__ == "__main__":
    print("🔍 Verifier Agent module loaded.")
    print("   To create an agent, call: create_verifier_agent(api_key='YOUR_API_KEY')")
