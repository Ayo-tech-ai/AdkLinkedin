"""
app.py
Streamlit web application for the AI Agritech Content Pipeline.
"""

import streamlit as st
import asyncio
import nest_asyncio
import os
import re

# Apply nest_asyncio
nest_asyncio.apply()

# ==================== STREAMLIT PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Agritech Content Pipeline",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
        padding-top: 1rem;
    }
    .info-box {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF9800;
        margin: 1rem 0;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #388E3C;
    }
    .chat-assistant {
        background-color: #F1F8E9;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #8BC34A;
    }
</style>
""", unsafe_allow_html=True)

def clean_agent_response(raw_response):
    """
    Clean the raw agent response to extract readable text.
    """
    response_str = str(raw_response)
    
    if not response_str or response_str == "None":
        return "No response received from the agent."
    
    # Check if it's an Event object
    if 'Event(model_version=' in response_str:
        try:
            # Method 1: Extract text between triple quotes
            text_matches = re.findall(r'text="""(.*?)"""', response_str, re.DOTALL)
            if text_matches:
                cleaned_text = text_matches[0].strip()
                if cleaned_text:
                    return cleaned_text
            
            # Method 2: Look for content parts
            if 'Content(parts=[' in response_str:
                # Find the main text content
                pattern = r'Part\(.*?text="""(.*?)""".*?\)'
                matches = re.findall(pattern, response_str, re.DOTALL)
                if matches:
                    return matches[0].strip()
            
            # Method 3: Fallback - clean up the string
            cleaned = response_str.replace('Event(model_version=', '')
            cleaned = cleaned.replace('Content(parts=[Part(text="""', '')
            cleaned = cleaned.replace('""",)], role=', '')
            cleaned = cleaned.replace('model', '')
            
            # Remove excessive whitespace
            cleaned = re.sub(r'\s+', ' ', cleaned)
            return cleaned.strip()
            
        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    # If it's just regular text
    else:
        # Clean up any remaining artifacts
        cleaned = response_str
        # Remove multiple newlines
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        return cleaned.strip()

# ==================== APP TITLE & DESCRIPTION ====================
st.markdown('<h1 class="main-header">🌾 AI Agritech Content Pipeline</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
<strong>🤖 Automated LinkedIn Post Generator</strong><br>
Research any AI-in-agriculture topic and produce fact-checked LinkedIn content using Google's Gemini AI with web search.
</div>
""", unsafe_allow_html=True)

# ==================== INITIALIZE SESSION STATE ====================
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'final_post' not in st.session_state:
    st.session_state.final_post = None

# ==================== SIDEBAR FOR INPUT ====================
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # API Key
    st.markdown("#### 🔑 Gemini API Key")
    st.markdown("""
    <div class="info-box" style="padding: 1rem; margin-bottom: 1rem;">
    <small>Get free API key:<br>
    <a href="https://aistudio.google.com/app/apikeys" target="_blank">Google AI Studio</a></small>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input(
        "Enter your Gemini API Key:",
        type="password",
        value=st.session_state.api_key,
        help="Your API key is only used for this session and not stored"
    )
    
    if api_key:
        st.session_state.api_key = api_key
    
    # Initialize Agent
    if st.button("🚀 Initialize AI Agent", use_container_width=True, type="primary"):
        if api_key:
            with st.spinner("Initializing AI Agent..."):
                try:
                    # Set API key
                    os.environ["GOOGLE_API_KEY"] = api_key
                    
                    # Import the workflow
                    from core.workflow import create_content_pipeline
                    
                    # Create the master agent
                    master_agent = create_content_pipeline()
                    
                    # Store in session state
                    st.session_state.master_agent = master_agent
                    st.session_state.agent_initialized = True
                    
                    st.success("✅ AI Agent initialized successfully!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error initializing agent: {str(e)}")
                    st.info("Make sure you have installed: pip install google-adk nest-asyncio")
        else:
            st.warning("⚠️ Please enter your API key first")
    
    st.markdown("---")
    
    # Topic input
    st.markdown("### 📝 Topic Selection")
    topic = st.text_input(
        "Enter agriculture/AI topic:",
        value="AI in pest and disease detection in plants",
        help="Example: 'Machine learning for crop yield prediction'"
    )
    
    # Generate button
    generate_disabled = not (st.session_state.get('agent_initialized', False) and topic.strip())
    
    generate_button = st.button(
        "🚀 Generate LinkedIn Post",
        disabled=generate_disabled,
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Clear conversation
    if st.button("🗑️ Clear Results", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.final_post = None
        st.rerun()
    
    # Info
    with st.expander("ℹ️ About"):
        st.markdown("""
        **How it works:**  
        1. **Research** the topic using Google Search  
        2. **Write** a professional LinkedIn post draft  
        3. **Iteratively verify & edit** the draft (max 3 cycles)  
        
        **Note:** Educational use only.
        Consult experts for serious agricultural advice.
        """)

# ==================== PIPELINE EXECUTION LOGIC ====================
async def run_pipeline_async(topic: str, api_key: str):
    """
    Execute the content pipeline using a master agent.
    """
    try:
        # Set API key
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Import ADK components
        from google.adk.runners import InMemoryRunner
        from core.workflow import create_content_pipeline
        
        # Create the master agent
        master_agent = create_content_pipeline()
        
        # Create runner
        runner = InMemoryRunner(agent=master_agent)
        
        # Execute the complete workflow
        query = f"""Create a fact-checked LinkedIn post about: {topic}

Follow this complete workflow:
1. RESEARCH: Search for current information, statistics, and case studies
2. WRITE: Create a professional LinkedIn post with hook, insights, applications, outlook, and hashtags
3. VERIFY: Fact-check the post for accuracy
4. ITERATE: Make corrections if needed

Return only the final LinkedIn post."""
        
        result = await runner.run_debug(query)
        
        # Clean and return result
        if result:
            return clean_agent_response(result)
        return None
        
    except Exception as e:
        st.error(f"Pipeline error: {str(e)}")
        raise

# ==================== MAIN CONTENT AREA ====================
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

# Status column
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 💬 LinkedIn Post Generator")
    
    if generate_button:
        if not st.session_state.get('agent_initialized', False):
            st.warning("⚠️ Please initialize the AI agent first (sidebar)")
        elif not topic.strip():
            st.warning("⚠️ Please enter a topic")
        else:
            with st.spinner("🌾 AI is generating your LinkedIn post... This takes 1-2 minutes."):
                try:
                    # Add topic to history
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": f"Topic: {topic}",
                        "timestamp": "Now"
                    })
                    
                    # Display user message
                    with st.chat_message("user"):
                        st.markdown(f"**Topic:** {topic}")
                    
                    # Run the async pipeline
                    final_post = asyncio.run(run_pipeline_async(topic, api_key))
                    
                    # Store in session state
                    st.session_state.final_post = final_post
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": final_post if final_post else "No post generated",
                        "timestamp": "Now"
                    })
                    
                    # Display agent response
                    if final_post:
                        with st.chat_message("assistant"):
                            st.markdown(f"**🌾 LinkedIn Post:** {final_post}")
                    
                    # Rerun to show the post in the text area
                    st.rerun()
                    
                except Exception as e:
                    error_msg = f"❌ Error generating post: {str(e)}"
                    st.error(error_msg)
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": "Now"
                    })

with col2:
    st.markdown("### 📊 Agent Status")
    
    if st.session_state.get('agent_initialized', False):
        st.markdown("""
        <div class="info-box">
        <strong>✅ Active</strong><br>
        • Model: Gemini 2.0 Flash Exp<br>
        • Tools: Google Search<br>
        • Status: Ready<br>
        • Workflow: Complete pipeline
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        total_messages = len(st.session_state.conversation_history)
        if total_messages > 0:
            st.caption(f"💬 {total_messages} messages in history")
    else:
        st.markdown("""
        <div class="warning-box">
        <strong>⏳ Setup Required</strong><br>
        1. Enter API key<br>
        2. Initialize agent<br>
        3. Enter topic<br>
        4. Generate post
        </div>
        """, unsafe_allow_html=True)

# Display conversation history
if st.session_state.conversation_history and not st.session_state.final_post:
    st.markdown("---")
    st.markdown("### 📜 Conversation History")
    
    for i, message in enumerate(st.session_state.conversation_history):
        if message["role"] == "user":
            st.markdown(f'**👤 You:** {message["content"]}')
        else:
            # Check if it's an error message
            if message["content"].startswith("❌"):
                st.error(message["content"])
            else:
                st.markdown(f'<div class="chat-assistant"><strong>🌾 Content Pipeline:</strong> {message["content"]}</div>', unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
<p>🌾 Built with Google ADK & Gemini AI | Deployed on Streamlit Cloud</p>
<p>⚠️ For educational purposes | Always verify with agricultural experts</p>
<p>🔒 Your API key is not stored on our servers</p>
</div>
""", unsafe_allow_html=True)

# Debug info
with st.expander("🔧 Debug Info (for troubleshooting)"):
    if st.session_state.get('agent_initialized', False):
        st.write("Agent Status: ✅ Initialized")
        st.write(f"Conversation History Length: {len(st.session_state.conversation_history)}")
    else:
        st.write("Agent Status: ❌ Not initialized")
    
    st.write(f"API Key Set: {'✅ Yes' if st.session_state.api_key else '❌ No'}")
    st.write(f"Environment API Key: {'✅ Set' if os.environ.get('GOOGLE_API_KEY') else '❌ Not set'}")
