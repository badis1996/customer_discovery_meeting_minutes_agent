# Customer Discovery Meeting Minutes Agent

An AI agent that processes sales call recordings from Apollo.io to generate customer discovery sheets automatically.

## Overview

This tool helps sales and customer success teams quickly extract valuable insights from customer calls recorded through Apollo.io. Instead of manually reviewing each call and taking notes, this AI agent:

1. Processes audio recordings from Apollo.io
2. Transcribes the conversation
3. Analyzes the discussion for key information
4. Generates a structured customer discovery sheet

## Features

- **Automated Transcription**: Convert audio recordings to text
- **Intelligent Analysis**: Extract key insights, pain points, and requirements
- **Customizable Templates**: Configure the discovery sheet format based on your needs
- **Integration with Apollo.io**: Seamlessly connect to your Apollo.io account
- **Export Options**: Generate discovery sheets in various formats (Markdown, CSV, PDF)

## Installation

```bash
# Clone the repository
git clone https://github.com/badis1996/customer_discovery_meeting_minutes_agent.git
cd customer_discovery_meeting_minutes_agent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your config
cp config.example.yml config.yml
# Edit config.yml with your settings
```

## Usage

### Basic Usage

```bash
python analyze.py --recording path/to/recording.mp3 --output discovery_sheet.md
```

### With Apollo.io Integration

```bash
python analyze.py --apollo-call-id 12345 --output discovery_sheet.md
```

### Batch Processing

```bash
python analyze.py --batch --apollo-date-range "2025-04-01,2025-04-30" --output-dir ./discovery_sheets/
```

## Configuration

Edit `config.yml` to customize:

- API keys and credentials
- Discovery sheet template
- Analysis parameters
- Export preferences

## Requirements

- Python 3.8+
- OpenAI API key or equivalent model access
- Apollo.io account with API access (for direct integration)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
