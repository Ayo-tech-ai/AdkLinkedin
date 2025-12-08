from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

# Import shared configuration from the core module
from core.config import retry_config

def create_editor_agent(api_key: str) -> Agent:
    """
    Factory function to create and return a configured Editor Agent.
    
    Args:
        api_key (str): The Gemini API key, passed from the main app.
    
    Returns:
        Agent: A configured Editor Agent instance.
    """
    editor_agent = Agent(
        name="editor_agent",
        model=Gemini(
            model="gemini-2.0-flash",  # Consistent with other agents
            retry_options=retry_config,
            api_key=api_key  # API key passed here
        ),
        description="Agent that edits LinkedIn posts based on verification feedback",
        instruction="""You are a precise editor for AI agriculture content.

CRITICAL REQUIREMENTS:
1. You MUST read the current LinkedIn post from: `context.state['linkedin_post']`
2. You MUST read the verification feedback from the previous agent
3. You MUST update the post in shared state: `context.state['linkedin_post'] = [Edited post]`

EDITING RULES:
1. Edit ONLY the specific sections mentioned in the verification feedback
2. Preserve the writer's style, tone, and overall structure
3. Make minimal changes to address the issues identified
4. Do not rewrite the entire post
5. Do not add new information not in the original research
6. Keep the post under 2,500 characters

EDITING PROCESS:
1. Read the current post from context.state['linkedin_post']
2. Read the verification feedback
3. Identify the exact lines/sections to edit
4. Make precise corrections
5. Update the post in context.state['linkedin_post']

OUTPUT FORMAT:
Return ONLY the edited LinkedIn post. Do not include explanations, notes, or markdown.""",
        tools=[],  # Editor agent doesn't need tools
    )
    return editor_agent

# Optional: Simple test if the file is run directly
if __name__ == "__main__":
    print("✏️  Editor Agent module loaded.")
    print("   To create an agent, call: create_editor_agent(api_key='YOUR_API_KEY')")
