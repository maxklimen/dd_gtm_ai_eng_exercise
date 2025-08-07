# DroneDeploy GTM AI Engineering Exercise

A Python application that generates personalized outbound emails for conference speakers at Digital Construction Week, inviting potential DroneDeploy customers to visit booth #42.

## Overview

This project:
1. Parses pre-scraped HTML files to extract speaker information
2. Enriches company data using Tavily API web search
3. Classifies companies using LLM (Builder/Owner/Partner/Competitor/Other)
4. Generates personalized emails for qualified prospects
5. Exports results to CSV format

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env_sample` to `.env` and add your API keys:
   ```bash
   cp .env_sample .env
   ```

4. Required API keys:
   - `TAVILY_API_KEY` - For web search and company enrichment
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - For classification and email generation

## Usage

Run the main script:
```bash
python main.py
```

The script will:
- Process all speaker HTML files from `in/scraped_pages/speakers/`
- Save intermediate results to `out/` directory
- Generate final CSV at `out/email_list.csv`

## Output

The final CSV includes:
- Speaker Name
- Speaker Title  
- Speaker Company
- Company Category (Builder/Owner/Partner/Competitor/Other)
- Email Subject
- Email Body

Emails are only generated for Builder and Owner categories.

## Project Structure

```
├── main.py              # Main orchestration script
├── utils/
│   ├── parser.py        # HTML parsing logic
│   ├── enrichment.py    # Tavily API integration
│   ├── classifier.py    # Company classification
│   └── email_generator.py # Email generation
├── in/
│   └── scraped_pages/   # Pre-scraped HTML files
├── out/                 # Output directory
└── cache/               # API response cache
```

## Performance

- Uses asyncio for concurrent API calls
- Caches Tavily API responses to avoid duplicates
- Processes ~300 speakers in under 2 hours