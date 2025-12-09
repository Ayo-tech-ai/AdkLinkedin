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
