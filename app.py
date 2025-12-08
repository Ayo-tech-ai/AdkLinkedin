import streamlit as st
import asyncio
import random
import nest_asyncio
from google.genai import types

# Import the workflow assembly function
from core.workflow import create_content_workflow
# Import the helper function to clean the final output
from core.config import clean_agent_response

# ==================== STREAMLIT PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Agritech Content Pipeline",
    page_icon="🌾",
    layout="wide"
)

# Apply nest_asyncio to allow async execution within Streamlit
nest_asyncio.apply()

# ==================== APP TITLE & DESCRIPTION ====================
st.title("🌾 AI Agritech Content Pipeline")
st.markdown("""
This automated pipeline researches any AI-in-agriculture topic and produces a fact-checked LinkedIn post.
**How it works:**  
1. **Research** the topic using Google Search  
2. **Write** a professional LinkedIn post draft  
3. **Iteratively verify & edit** the draft (max 3 cycles) until it's factually accurate  
""")
st.divider()

# ==================== SIDEBAR FOR INPUT ====================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Topic input
    topic = st.text_input(
        "Enter your agriculture/AI topic:",
        value="AI in pest and disease detection in plants",
        help="Example: 'Machine learning for crop yield prediction'"
    )
    
    # Generate button
    generate_button = st.button(
        "🚀 Generate LinkedIn Post",
        type="primary",
        use_container_width=True
    )
    
    st.divider()
    st.caption("""
    **Note:**  
    • A full run takes 60-120 seconds.  
    • Please be patient after clicking the button.  
    • The free tier allows limited requests per day.
    """)

# ==================== MAIN CONTENT AREA ====================
# Initialize session state for the final result
if "final_post" not in st.session_state:
    st.session_state.final_post = None

# Display the final post from a previous run if it exists
if st.session_state.final_post:
    st.header("📄 Your Generated LinkedIn Post")
    st.text_area(
        "Copy your post below:",
        st.session_state.final_post,
        height=300
    )
    st.caption(f"Character count: {len(st.session_state.final_post)}")
    st.divider()

# ==================== PIPELINE EXECUTION LOGIC ====================
async def run_pipeline_async(topic: str, api_key: str):
    """
    Async function to execute the complete content pipeline.
    This is the bridge between Streamlit (sync) and the ADK pipeline (async).
    """
    # 1. Create the workflow runner using the API key from secrets
    runner, session_service = create_content_workflow(api_key)
    
    # 2. Create a unique session ID for this run
    random_session_id = f"streamlit_session_{random.randint(1000, 9999)}"
    
    # 3. Prepare the input as a Content object
    query = f"Research and create a LinkedIn post about: {topic}"
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    # 4. Execute the pipeline and collect all events
    all_events = []
    async for event in runner.run_async(
        user_id="streamlit_user",
        session_id=random_session_id,
        new_message=content
    ):
        all_events.append(event)
    
    # 5. Extract the final response from the events
    final_response = None
    for event in reversed(all_events):
        if hasattr(event, 'is_final_response') and event.is_final_response():
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_response = part.text
                        break
            break
    
    # 6. Clean and return the final post
    if final_response:
        return clean_agent_response(final_response)
    return None

# ==================== HANDLE BUTTON CLICK ====================
if generate_button:
    # Validate input
    if not topic.strip():
        st.error("Please enter a topic.")
        st.stop()
    
    # Check for API key in secrets
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("""
        **API Key Missing.**  
        Please add your Gemini API key to `.streamlit/secrets.toml` file:
        ```
        GOOGLE_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
        ```
        """)
        st.stop()
    
    # Get the API key from Streamlit secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # Display a status container for the pipeline run
    with st.status("🤖 **Running AI Pipeline...** This will take 1-2 minutes.", expanded=True) as status:
        st.write("1. **Researching** the topic...")
        st.write("2. **Writing** the first draft...")
        st.write("3. **Verifying & editing** the draft (this is the iterative loop)...")
        
        try:
            # Execute the async pipeline using asyncio.run()
            final_post = asyncio.run(run_pipeline_async(topic, api_key))
            
            if final_post:
                # Update session state with the result
                st.session_state.final_post = final_post
                status.update(label="✅ **Pipeline Complete!**", state="complete", expanded=False)
                st.rerun()  # Rerun the app to display the new post
            else:
                status.update(label="❌ **Pipeline completed but no output was generated.**", state="error")
                st.error("The pipeline ran but did not return a post. Check the logs for errors.")
                
        except Exception as e:
            status.update(label="❌ **Pipeline Execution Failed**", state="error")
            st.exception(e)  # Display the full error traceback

# ==================== FOOTER ====================
st.divider()
st.caption("""
    Built with Google's Agent Development Kit (ADK) & Streamlit.  
    The pipeline uses Gemini 2.5 flash lite for AI and Google Search for research.
""")
