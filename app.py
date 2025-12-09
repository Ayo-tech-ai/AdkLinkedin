import streamlit as st
import asyncio
import nest_asyncio
import os

# Import the workflow
from core.workflow import create_content_pipeline
from core.config import clean_agent_response

# Apply nest_asyncio
nest_asyncio.apply()

# ==================== STREAMLIT PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Agritech Content Pipeline",
    page_icon="🌾",
    layout="wide"
)

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
    
    # API Key input
    api_key = st.text_input(
        "Enter Gemini API Key:",
        type="password",
        help="Get from https://aistudio.google.com/app/apikeys"
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
if "final_post" not in st.session_state:
    st.session_state.final_post = None

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
    Execute the content pipeline using InMemoryRunner.
    """
    try:
        # Set API key
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Import ADK components
        from google.adk.runners import InMemoryRunner
        
        # Create the pipeline
        workflow_agent = create_content_pipeline()
        
        # Create runner with search tools
        runner = InMemoryRunner(agent=workflow_agent)
        
        # Execute the pipeline
        query = f"Research and create a LinkedIn post about: {topic}"
        result = await runner.run_debug(query)
        
        # Clean and return result
        if result:
            return clean_agent_response(result)
        return None
        
    except Exception as e:
        st.error(f"Pipeline error: {str(e)}")
        raise

# ==================== HANDLE BUTTON CLICK ====================
if generate_button:
    if not topic.strip():
        st.error("Please enter a topic.")
        st.stop()
    
    if not api_key:
        st.error("Please enter your Gemini API key.")
        st.stop()
    
    with st.status("🤖 **Running AI Pipeline...** This will take 1-2 minutes.", expanded=True) as status:
        st.write("1. **Researching** the topic...")
        st.write("2. **Writing** the first draft...")
        st.write("3. **Verifying & editing** the draft...")
        
        try:
            final_post = asyncio.run(run_pipeline_async(topic, api_key))
            
            if final_post:
                st.session_state.final_post = final_post
                status.update(label="✅ **Pipeline Complete!**", state="complete", expanded=False)
                st.rerun()
            else:
                status.update(label="❌ **No output generated.**", state="error")
                
        except Exception as e:
            status.update(label="❌ **Pipeline Execution Failed**", state="error")
            st.error(f"Error: {str(e)}")

# ==================== FOOTER ====================
st.divider()
st.caption("""
    Built with Google's Agent Development Kit (ADK) & Streamlit.  
    The pipeline uses Gemini 2.0 Flash for AI and Google Search for research.
""")
