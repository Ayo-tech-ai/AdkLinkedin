from google.adk.agents import LoopAgent, SequentialAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

# Import the agent factory functions
from agents.research_agent import create_research_agent
from agents.writer_agent import create_writer_agent
from agents.verifier_agent import create_verifier_agent
from agents.editor_agent import create_editor_agent

def create_content_workflow(api_key: str):
    """
    Creates and returns the complete agent workflow (SequentialAgent) and its runner.
    
    This function:
    1. Creates all four individual agents using the provided API key.
    2. Puts the Verifier and Editor into a LoopAgent (refinement loop).
    3. Chains Research -> Writer -> Loop into a SequentialAgent (main pipeline).
    4. Creates a Runner and SessionService for the pipeline.
    
    Args:
        api_key (str): The Gemini API key to configure all agents.
    
    Returns:
        tuple: (runner, session_service) - The runner to execute the pipeline and its session service.
    """
    # 1. Create all four agents using the shared API key
    print("   [1/4] Creating Research Agent...")
    research_agent = create_research_agent(api_key)
    
    print("   [2/4] Creating Writer Agent...")
    writer_agent = create_writer_agent(api_key)
    
    print("   [3/4] Creating Verifier Agent...")
    verifier_agent = create_verifier_agent(api_key)
    
    print("   [4/4] Creating Editor Agent...")
    editor_agent = create_editor_agent(api_key)
    
    # 2. Create the refinement loop (Verifier <-> Editor)
    print("   Building Refinement Loop...")
    refinement_loop = LoopAgent(
        name="refinement_loop",
        sub_agents=[verifier_agent, editor_agent],
        max_iterations=3,
        description="Iteratively verifies and edits content until approved or max iterations reached."
    )
    
    # 3. Create the main sequential pipeline
    print("   Assembling Main Pipeline...")
    content_workflow = SequentialAgent(
        name="linkedin_pipeline",
        sub_agents=[research_agent, writer_agent, refinement_loop],
        description="1. Researches topic -> 2. Writes first draft -> 3. Iteratively refines draft"
    )
    
    # 4. Create the runner and session service
    print("   Configuring Runner...")
    session_service = InMemorySessionService()
    runner = Runner(
        agent=content_workflow,
        app_name="ai_agriculture_content",
        session_service=session_service
    )
    
    print("✅ Pipeline assembly complete.")
    return runner, session_service

# Optional: Test code if run directly (requires API key)
if __name__ == "__main__":
    print("🏗️  Workflow assembly module loaded.")
    print("   To create the pipeline, call: runner, session_service = create_content_workflow(api_key='YOUR_KEY')")
    print("   WARNING: Running this directly will make actual API calls if a valid key is provided.")
