import re

def clean_agent_response(raw_response):
    """
    Clean the raw agent response to extract readable text.
    """
    response_str = str(raw_response)
    
    if not response_str or response_str == "None":
        return "No response received."
    
    # Try to extract text between triple quotes
    text_matches = re.findall(r'text="""(.*?)"""', response_str, re.DOTALL)
    if text_matches:
        cleaned_text = text_matches[0].strip()
        if cleaned_text:
            return cleaned_text
    
    # Fallback: extract from content parts
    if 'Content(parts=[' in response_str:
        pattern = r'Part\(.*?text="""(.*?)""".*?\)'
        matches = re.findall(pattern, response_str, re.DOTALL)
        if matches:
            return matches[0].strip()
    
    # Return cleaned string
    cleaned = response_str
    cleaned = cleaned.replace('Event(model_version=', '')
    cleaned = cleaned.replace('Content(parts=[Part(text="""', '')
    cleaned = cleaned.replace('""",)], role=', '')
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()
