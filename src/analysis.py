from typing import Dict, Any, List
import openai
import json


def analyze_transcript(transcript_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the transcript using OpenAI's API to extract insights.
    
    Args:
        transcript_data: Dictionary containing transcript and metadata
        config: Application configuration
        
    Returns:
        Dictionary containing analysis results
    """
    # Configure OpenAI client
    openai.api_key = config['api']['openai']['api_key']
    model = config['api']['openai'].get('model', 'gpt-4')
    
    # Get the transcript text
    transcript = transcript_data.get('transcript', '')
    
    # Prepare the prompt based on discovery sheet template
    discovery_config = config.get('discovery_sheet', {})
    sections = discovery_config.get('sections', [])
    
    # Build a structured prompt
    prompt = build_analysis_prompt(transcript, sections)
    
    # Call the OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert sales analyst specializing in analyzing customer discovery calls. Your task is to extract relevant information from a sales call transcript and organize it into a structured format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for more deterministic results
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        content = response.choices[0].message.content
        analysis_result = json.loads(content)
        
        # Combine with transcript data
        return {
            "analysis": analysis_result,
            "transcript_data": transcript_data
        }
        
    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")


def build_analysis_prompt(transcript: str, sections: List[Dict[str, Any]]) -> str:
    """Build a structured prompt for the OpenAI API based on discovery sheet sections.
    
    Args:
        transcript: The transcript text
        sections: List of section configurations from the discovery sheet template
        
    Returns:
        Formatted prompt
    """
    # Build the JSON schema based on the configured sections
    schema_parts = []
    for section in sections:
        fields_schema = []
        for field in section.get('fields', []):
            field_name = field.get('name')
            description = field.get('description', '')
            fields_schema.append(f'"{field_name}": "string // {description}"')
        
        section_schema = f'"{section["title"]}": {{
            {",\n            ".join(fields_schema)}
        }}'
        schema_parts.append(section_schema)
    
    json_schema = "{
    " + ",\n    ".join(schema_parts) + "\n}"
    
    # Build the prompt
    prompt = f"""Below is a transcript from a sales discovery call. Please analyze it carefully and extract the relevant information according to the specified structure.\n\nTRANSCRIPT:\n\n{transcript}\n\nPlease extract information from this transcript and provide it in the following JSON structure. If information for a field is not available in the transcript, use null or provide your best guess based on context:\n\n{json_schema}\n\nAdditional guidelines:\n1. Focus on extracting factual information rather than making assumptions\n2. Include verbatim quotes when relevant in the 'key_quotes' field\n3. For the 'challenges' and 'needs' fields, try to identify both explicit statements and implicit needs revealed in the conversation\n4. When extracting information about timeline, budget, or decision process, note the specific context in which this information was shared\n5. Organize 'next_steps' in a clear, actionable format\n\nProvide your response as a valid JSON object matching the structure above."""
    
    return prompt
