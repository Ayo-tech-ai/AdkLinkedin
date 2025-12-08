from google.adk.tools import FunctionTool
from google.genai import types
import re

# ==================== RETRY CONFIGURATION ====================
# Defines how the agents retry failed API calls
retry_config = types.HttpRetryOptions(
    attempts=3,
    exp_base=2,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# ==================== HELPER FUNCTION ====================
def clean_agent_response(raw_response):
    """
    Clean agent response to extract readable text from Event objects.
    This is the ONLY extraction function needed.
    """
    response_str = str(raw_response)

    # If it's already clean text
    if not response_str.startswith('Event('):
        return response_str.strip()

    # Extract text from Event object - Method 1: Triple quotes
    text_matches = re.findall(r'text="""(.*?)"""', response_str, re.DOTALL)
    if text_matches:
        return text_matches[0].strip()

    # Method 2: Look for agent name prefix
    lines = response_str.split('\n')
    cleaned_lines = []
    for line in lines:
        if line and not line.startswith('Event(') and not line.startswith('User >'):
            # Remove agent name prefixes if present
            for agent_name in ['research_agent', 'writer_agent', 'verifier_agent', 'editor_agent']:
                if agent_name + ' >' in line:
                    line = line.split(agent_name + ' >')[-1].strip()
                    break
            cleaned_lines.append(line.strip())

    return '\n'.join(cleaned_lines) if cleaned_lines else response_str

# ==================== LOOP EXIT TOOL ====================
# Define the function that implements the tool logic
def exit_refinement_loop():
    """Call this tool ONLY when the content is fully approved.
    This signals the LoopAgent to stop iterating and output the final result."""
    return {"status": "approved", "message": "Content is factually accurate."}

# Create the tool instance (SINGLE DEFINITION - will be reused)
approve_and_exit_tool = FunctionTool(
    func=exit_refinement_loop,  # This is the key argument
)

# Optional: Print statement for debugging when the module loads
if __name__ == "__main__":
    print("✅ Core configuration module loaded successfully.")
    print(f"   Retry config: {retry_config}")
    print(f"   Tool created: {approve_and_exit_tool.name}")
