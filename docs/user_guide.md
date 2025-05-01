# Customer Discovery Meeting Minutes Agent - User Guide

## Introduction

The Customer Discovery Meeting Minutes Agent is a tool designed for sales teams to automatically extract insights from call recordings. This guide will help you get started with using the tool effectively.

## Installation

### Using Docker (Recommended)

The easiest way to get started is using Docker:

```bash
# Clone the repository
git clone https://github.com/badis1996/customer_discovery_meeting_minutes_agent.git
cd customer_discovery_meeting_minutes_agent

# Create a .env file with your API keys
cat > .env << EOL
OPENAI_API_KEY=your_openai_api_key_here
APOLLO_API_KEY=your_apollo_api_key_here
APOLLO_TEAM_ID=your_apollo_team_id_here
EOL

# Start the application
docker-compose up -d
```

The application will be available at http://localhost:8000.

### Manual Installation

If you prefer a manual installation:

```bash
# Clone the repository
git clone https://github.com/badis1996/customer_discovery_meeting_minutes_agent.git
cd customer_discovery_meeting_minutes_agent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your settings
cp config.example.yml config.yml
# Edit config.yml with your API keys and preferences

# Start the application
python main.py
```

## Getting Started

### Using the Web Interface

1. Open your browser and navigate to http://localhost:8000
2. Choose one of the two options:
   - **Upload Recording**: Upload a call recording file directly
   - **Apollo.io Recording**: Enter an Apollo.io call ID to process a recording from your account
3. Select your preferred output format (JSON, Markdown, CSV)
4. Click "Analyze Recording" to start the process
5. Wait for the analysis to complete
6. Review the generated discovery sheet and download it if needed

### Using the Command Line

The command line interface provides more options for batch processing and integration:

```bash
# Analyze a local recording file
python analyze.py --recording path/to/recording.mp3 --output discovery_sheet.md

# Analyze an Apollo.io recording by ID
python analyze.py --apollo-call-id 12345 --output discovery_sheet.json

# Batch process multiple recordings in a directory
python analyze.py --batch --input-dir ./recordings/ --output-dir ./discovery_sheets/

# Batch process Apollo.io recordings from a date range
python analyze.py --batch --apollo-date-range "2025-04-01,2025-04-30" --output-dir ./discovery_sheets/
```

## Understanding the Discovery Sheet

The generated discovery sheet is organized into sections that help you quickly understand the key aspects of the customer conversation:

### Company Information

Basic details about the prospect's company, including name, industry, size, and key decision-makers mentioned during the call.

### Current Situation

Information about the prospect's current tools, processes, and challenges. This section helps you understand their pain points and areas where your solution could add value.

### Needs and Requirements

Both explicit needs (directly stated by the prospect) and implicit needs (inferred from the conversation). This section also includes any success metrics mentioned.

### Buying Process

Details about the prospect's purchasing timeline, budget constraints, decision-making process, and competing solutions they might be considering.

### Next Steps

Action items agreed upon during the call, follow-up dates, and additional contacts to involve in the process.

### Notes

Important quotes from the call and any additional observations that don't fit in the other categories.

### Transcript

A time-stamped transcript of the entire conversation, showing who said what and when.

## Customizing the Analysis

You can customize how the discovery sheet is structured by editing the `config.yml` file. In the `discovery_sheet` section, you can:

- Add or remove sections
- Modify field names and descriptions
- Change the order of sections and fields

Example:

```yaml
discovery_sheet:
  sections:
    - title: "Technical Requirements"
      fields:
        - name: "integration_needs"
          description: "Required integrations with existing systems"
        - name: "security_requirements"
          description: "Security and compliance requirements"
```

## Tips for Best Results

1. **Recording Quality**: Ensure call recordings have good audio quality with minimal background noise
2. **Call Structure**: Following a consistent discovery call structure will yield more structured results
3. **Speaking Clearly**: Clear articulation helps the transcription accuracy
4. **Mention Key Information**: Make sure important details (company name, industry, etc.) are explicitly mentioned during the call
5. **Review and Edit**: Always review the generated discovery sheet before sharing it with your team

## Troubleshooting

### Common Issues

1. **Transcription Errors**: If the transcription has many errors, try:
   - Converting the audio to a higher quality format
   - Using the `convert_audio_format` utility before analysis
   - Ensuring the recording has minimal background noise

2. **Missing Information**: If the analysis is missing key information:
   - Make sure the information was explicitly mentioned in the call
   - Check if your `config.yml` includes the appropriate fields
   - Consider running the analysis with a more powerful language model

3. **API Errors**: If you encounter API errors:
   - Verify your API keys are correct
   - Check your rate limits for both OpenAI and Apollo.io
   - Ensure your network connection is stable

### Getting Help

If you encounter issues not covered here:

1. Check the logs in the `logs` directory
2. Review the issue tracker on GitHub
3. Submit a new issue with detailed information about the problem

## Advanced Usage

### API Integration

You can integrate the Customer Discovery Meeting Minutes Agent with your existing systems using the REST API:

```python
import requests
import json

# Upload and analyze a recording
files = {'file': open('call_recording.mp3', 'rb')}
data = {'output_format': 'json'}
response = requests.post('http://localhost:8000/api/analyze/upload', files=files, data=data)
job_id = response.json()['job_id']

# Check job status
status_response = requests.get(f'http://localhost:8000/api/status/{job_id}')
result = status_response.json()

# When completed, download the result
if result['status'] == 'completed':
    download_url = f"http://localhost:8000{result['result']['output_url']}"
    discovery_sheet = requests.get(download_url).content
    # Process the discovery sheet...
```

## Apollo.io Integration

To use the Apollo.io integration, you'll need an Apollo.io account with API access. Follow these steps:

1. Log in to your Apollo.io account
2. Navigate to Settings > API
3. Generate a new API key with permissions for accessing call recordings
4. Note your Team ID from the API page
5. Add these credentials to your `config.yml` file

```yaml
api:
  apollo:
    api_key: "your_apollo_api_key_here"
    team_id: "your_apollo_team_id"
```

## Security Considerations

1. **API Keys**: Keep your API keys secure and never commit them to version control
2. **Data Retention**: Be mindful of how long you retain call recordings and transcripts
3. **Access Control**: Restrict access to the application and discovery sheets to authorized personnel
4. **Compliance**: Ensure your use of call recordings complies with relevant regulations

## License

This project is licensed under the MIT License - see the LICENSE file for details.
