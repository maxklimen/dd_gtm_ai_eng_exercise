# DroneDeploy GTM AI Engineering Exercise

A Python application that generates personalized outbound emails for conference speakers at Digital Construction Week, inviting potential DroneDeploy customers to visit booth #42.

## 🎯 Key Results

- **398 Speakers** successfully extracted
- **472 Sessions** captured (60 speakers presenting multiple sessions)
- **100% Data Coverage** for sessions and profile images
- **Enhanced Personalization** using session topics in emails

## Overview

This project:
1. Parses pre-scraped HTML files to extract comprehensive speaker information
2. Captures conference sessions, profile images, and contact details
3. Enriches company data using Tavily API web search
4. Classifies companies using LLM (Builder/Owner/Partner/Competitor/Other)
5. Generates personalized emails that reference speaker's conference talks
6. Exports results to CSV format

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
- Email Subject (personalized with session references)
- Email Body (3-4 sentences with booth #42 CTA)

Emails are only generated for Builder and Owner categories.

### Enhanced Data Structure

Each speaker record now includes:
```json
{
  "speaker_id": "abbey-gore",
  "name": "Abbey Gore",
  "company": "Laing O'Rourke",
  "job_title": "Digital Lead",
  "sessions": [
    {
      "title": "A digital shot in the arm for hospital delivery",
      "url": "https://..."
    }
  ],
  "image_url": "https://...Abbey-Gore.png"
}
```

## Project Structure

```
├── main.py                    # Main orchestration script
├── utils/
│   ├── parser.py             # Enhanced HTML parsing (sessions, images)
│   ├── enrichment.py         # Tavily API integration
│   ├── classifier.py         # Company classification
│   └── email_generator.py    # Session-aware email generation
├── in/
│   └── scraped_pages/        # 398 pre-scraped HTML files
│       └── speakers/
├── out/                      # Output directory
│   ├── speakers_raw.json     # Parser output
│   ├── speakers_enriched.json # With company data
│   ├── speakers_classified.json # With categories
│   └── email_list.csv        # Final output
└── cache/                    # API response cache
```

## Session Distribution

| Sessions | Speakers | Percentage | Priority |
|----------|----------|------------|----------|
| 1 session | 338 | 84.9% | Standard |
| 2 sessions | 48 | 12.1% | High |
| 3 sessions | 10 | 2.5% | Very High |
| 4 sessions | 2 | 0.5% | Top Priority |

Multi-session speakers are likely decision-makers and influencers.

## Performance

- Uses asyncio for concurrent API calls
- Caches Tavily API responses to avoid duplicates
- Processes 398 speakers in approximately 2-3 minutes
- 100% extraction success rate

## Testing

Test the enhanced parser without dependencies:
```bash
python test_enhanced_parser.py
```

This will verify:
- All 398 speakers are extracted
- Sessions are captured correctly
- Image URLs are present
- Edge cases are handled