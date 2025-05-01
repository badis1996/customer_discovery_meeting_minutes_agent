# Integration Guide

## Overview

This guide explains how to integrate the Customer Discovery Meeting Minutes Agent with your existing systems and workflows.

## API Integration

The Customer Discovery Meeting Minutes Agent provides a RESTful API that you can use to automate the processing of call recordings. The API is available at `http://localhost:8000/api` when running the application locally.

### Authentication

Currently, the API does not require authentication for local usage. For production deployments, you should implement authentication middleware appropriate for your environment.

### API Endpoints

#### Upload and Analyze a Recording

Endpoint: `POST /api/analyze/upload`

Parameters:
- `file`: The audio file to analyze (multipart/form-data)
- `output_format`: The desired output format (json, markdown, csv, or pdf)

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "progress": 0.0
}
```

#### Analyze an Apollo.io Recording

Endpoint: `POST /api/analyze/apollo`

Parameters (JSON):
```json
{
  "apollo_call_id": "12345",
  "output_format": "json"
}
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "fetching_recording",
  "progress": 0.1
}
```

#### Check Job Status

Endpoint: `GET /api/status/{job_id}`

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 1.0,
  "result": {
    "discovery_sheet": { /* Discovery sheet data */ },
    "output_path": "./output/discovery_sheet_550e8400-e29b-41d4-a716-446655440000.json",
    "output_url": "/download/discovery_sheet_550e8400-e29b-41d4-a716-446655440000.json"
  }
}
```

Possible status values:
- `queued`: Job is in the queue
- `fetching_recording`: Fetching recording from Apollo.io
- `transcribing`: Transcribing audio
- `analyzing`: Analyzing transcript
- `generating_report`: Generating discovery sheet
- `completed`: Analysis completed
- `failed`: Analysis failed

#### Download Result

Endpoint: `GET /download/{filename}`

Response: The discovery sheet file

### Example API Usage

#### Python

```python
import requests
import time
import json

API_BASE_URL = 'http://localhost:8000/api'

# Upload and analyze a recording
def analyze_recording(file_path, output_format='json'):
    files = {'file': open(file_path, 'rb')}
    data = {'output_format': output_format}
    
    response = requests.post(f'{API_BASE_URL}/analyze/upload', files=files, data=data)
    response.raise_for_status()
    
    return response.json()['job_id']

# Check job status
def check_job_status(job_id):
    response = requests.get(f'{API_BASE_URL}/status/{job_id}')
    response.raise_for_status()
    
    return response.json()

# Wait for job to complete
def wait_for_completion(job_id, poll_interval=2):
    while True:
        status = check_job_status(job_id)
        
        if status['status'] == 'completed':
            return status['result']
        elif status['status'] == 'failed':
            raise Exception(f"Analysis failed: {status.get('error')}")
        
        print(f"Status: {status['status']} ({status['progress']*100:.0f}%)")
        time.sleep(poll_interval)

# Download result
def download_result(output_url):
    response = requests.get(f'http://localhost:8000{output_url}')
    response.raise_for_status()
    
    return response.content

# Main process
def process_recording(file_path, output_format='json'):
    # Start analysis
    job_id = analyze_recording(file_path, output_format)
    print(f"Analysis started with job ID: {job_id}")
    
    # Wait for completion
    result = wait_for_completion(job_id)
    print("Analysis completed!")
    
    # Download result
    discovery_sheet = download_result(result['output_url'])
    
    # Save result to file
    output_filename = f"discovery_sheet_{job_id}.{output_format}"
    with open(output_filename, 'wb') as f:
        f.write(discovery_sheet)
    
    print(f"Discovery sheet saved to {output_filename}")
    
    return result['discovery_sheet']

# Example usage
if __name__ == "__main__":
    discovery_sheet = process_recording('path/to/recording.mp3', 'json')
    print(json.dumps(discovery_sheet, indent=2))
```

#### JavaScript

```javascript
async function analyzeRecording(filePath, outputFormat = 'json') {
  const formData = new FormData();
  formData.append('file', await fetch(filePath).then(res => res.blob()));
  formData.append('output_format', outputFormat);
  
  const response = await fetch('http://localhost:8000/api/analyze/upload', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.job_id;
}

async function checkJobStatus(jobId) {
  const response = await fetch(`http://localhost:8000/api/status/${jobId}`);
  return response.json();
}

async function waitForCompletion(jobId, pollInterval = 2000) {
  while (true) {
    const status = await checkJobStatus(jobId);
    
    if (status.status === 'completed') {
      return status.result;
    } else if (status.status === 'failed') {
      throw new Error(`Analysis failed: ${status.error}`);
    }
    
    console.log(`Status: ${status.status} (${Math.round(status.progress*100)}%)`);
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
}

async function downloadResult(outputUrl) {
  const response = await fetch(`http://localhost:8000${outputUrl}`);
  return response.blob();
}

async function processRecording(filePath, outputFormat = 'json') {
  // Start analysis
  const jobId = await analyzeRecording(filePath, outputFormat);
  console.log(`Analysis started with job ID: ${jobId}`);
  
  // Wait for completion
  const result = await waitForCompletion(jobId);
  console.log('Analysis completed!');
  
  // Download result
  const discoverySheet = await downloadResult(result.output_url);
  
  return {
    discoverySheet: result.discovery_sheet,
    downloadBlob: discoverySheet
  };
}

// Example usage
processRecording('path/to/recording.mp3', 'json')
  .then(result => {
    console.log(result.discoverySheet);
    // Save or display the result
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

## Apollo.io Integration

### Prerequisites

1. An active Apollo.io account with API access
2. Admin privileges to generate API keys
3. Call recording enabled for your Apollo.io account

### Setting Up Apollo.io Integration

1. Log in to your Apollo.io account
2. Navigate to Settings > API
3. Generate a new API key with permissions for accessing call recordings
4. Note your Team ID from the API page

### Configuring the Integration

Add your Apollo.io credentials to the `config.yml` file:

```yaml
api:
  apollo:
    api_key: "your_apollo_api_key_here"
    team_id: "your_apollo_team_id"
```

Alternatively, set these as environment variables when running the Docker container:

```bash
export APOLLO_API_KEY="your_api_key"
export APOLLO_TEAM_ID="your_team_id"
```

### Automatic Processing with Webhooks

Apollo.io supports webhooks that can notify your system when a new call recording is available. To set this up:

1. Deploy the Customer Discovery Meeting Minutes Agent on a server with a public endpoint
2. Configure your Apollo.io webhook settings to send call recording events to your API endpoint
3. Implement a webhook handler in your deployment that triggers analysis when a new recording is available

## Salesforce Integration

You can integrate the Customer Discovery Meeting Minutes Agent with Salesforce to automatically add discovery sheets to your Salesforce records. To enable this integration:

1. Uncomment and configure the Salesforce integration section in `config.yml`:

```yaml
integrations:
  salesforce:
    enabled: true
    username: "your_username"
    password: "your_password"
    security_token: "your_security_token"
    domain: "login" # or "test" for sandbox
```

2. Customize the Salesforce mapping in your code to determine how discovery sheet fields should map to Salesforce fields. 

## Other CRM Integrations

For integrations with other CRM systems (HubSpot, Zoho, etc.), you can use the API to implement custom integrations that fit your workflow.

## Questions and Support

If you need help with integration, please open an issue on the GitHub repository or contact the project maintainers.