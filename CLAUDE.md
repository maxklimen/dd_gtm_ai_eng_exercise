# DroneDeploy GTM Exercise - Project Context

## Overview
This is a take-home exercise for DroneDeploy to generate personalized outbound emails for conference speakers at Digital Construction Week. The goal is to invite potential customers to visit booth #42 for a demo and free gift.

## Task Requirements
- **Target Audience**: Conference speakers who are potential DroneDeploy customers
- **Customer Categories**:
  - **Builders**: General contractors, specialty contractors, engineering firms (those building things)
  - **Owners**: Those getting things built for them
  - **Exclude**: Competitors and potential partners
- **Time Limit**: 2 hours
- **Conference**: Digital Construction Week (already passed - outputs won't be used)

## Technical Requirements
- Python with asyncio for concurrent operations
- LLM integration (OpenAI/Anthropic/Google)
- Output: CSV file with speaker details and personalized emails
- Environment variables for API keys

## Data Structure
Pre-scraped HTML files are in `in/scraped_pages/speakers/[speaker-name]/index.html`

Each speaker page contains:
```html
<div class="speaker-details">
    <p><strong>Name:</strong> [Speaker Name]</p>
    <p><strong>Company:</strong> [Company Name]</p>
    <p><strong>Job Title:</strong> [Job Title]</p>
</div>

<div class="speaker-sessions">
    <h3>Sessions</h3>
    <ul>
        <li><a href="[session-url]">[Session Title]</a></li>
    </ul>
</div>

<meta property="og:image" content="[speaker-image-url]"/>
```

### Enhanced Data Extraction
- **398 speakers** successfully parsed
- **472 total sessions** (60 speakers presenting multiple sessions)
- **All speakers have profile images**
- **12 speakers** with empty job titles (3%)

## Implementation Plan (Iterative Approach)

### Step 1: Extract Speaker Data ✅ COMPLETED
- Parse HTML files using BeautifulSoup
- Extract: Name, Company, Job Title, Sessions, Image URLs
- Save to JSON for processing
- Handle edge cases (missing data, empty job titles)
- **Result**: 398 speakers with 472 sessions extracted

### Step 2: Enrich with Tavily API
- Search for company + construction industry context
- Cache results to avoid duplicate API calls
- Get company descriptions, industry focus, recent news

### Step 3: Classify Companies
- Use LLM to classify based on enriched data
- Categories: Builder, Owner, Partner, Competitor, Other
- Include reasoning for classification

### Step 4: Generate Personalized Emails
- Create compelling subject lines
- Personalize body based on:
  - Company category
  - Person's role/title
  - Session topics (reference their talks)
  - Company's specific needs
- Emphasize booth #42 and free gift
- Keep professional but engaging tone
- Multi-session speakers get special recognition

### Step 5: Export to CSV
- Required columns:
  - Speaker Name
  - Speaker Title
  - Speaker Company
  - Company Category
  - Email Subject
  - Email Body

## Project Structure
```
dd_gtm_ai_eng_exercise/
├── .env_sample          # API key template
├── CLAUDE.md           # This file
├── main.py             # Main orchestration script
├── README.md           # User instructions
├── requirements.txt    # Python dependencies
├── in/
│   └── scraped_pages/  # Pre-scraped HTML files
├── out/
│   └── email_list.csv  # Final output
└── utils/
    ├── __init__.py
    ├── parser.py       # HTML parsing logic
    ├── enrichment.py   # Tavily API integration
    ├── classifier.py   # Company classification
    └── email_generator.py  # Email generation
```

## API Keys Required
- `TAVILY_API_KEY`: For web search and enrichment
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: For LLM classification and generation

## Performance Considerations
- Use asyncio for concurrent API calls
- Cache Tavily results to avoid duplicates
- Batch LLM requests where possible
- Show progress with tqdm
- Handle rate limits gracefully

## Email Strategy
- **Builders**: Focus on efficiency, ROI, project management
- **Owners**: Focus on visibility, cost control, project oversight
- **Tone**: Professional, value-focused, specific benefits
- **CTA**: Visit booth #42 for demo and free gift

## Working with this Project

**Claude Code will**:
- Read this file automatically each session (persistent memory)
- Check `@in/DD_TASK.md` for requirements alignment
- Ask you to update this file when we make decisions

**This file tracks**: Progress, decisions, and context across sessions.

## Progress Tracker

### Completed
- ✅ Project structure created
- ✅ Enhanced parser with session & image extraction (398 speakers, 472 sessions)
- ✅ All utility modules implemented (parser, enrichment, classifier, email_generator)
- ✅ Main orchestration script ready
- ✅ Email generator updated to reference speaker sessions
- ✅ Documentation updated with latest findings

### Next Steps
- 🔄 Install dependencies: `pip install -r requirements.txt`
- 🔄 Configure API keys in `.env` file
- 🔄 Run full pipeline: `python3 main.py`
- 🔄 Review generated emails in `out/email_list.csv`

## Implementation Decisions

### Data Source
- Using pre-scraped HTML files in `in/scraped_pages/`
- Saves time, ensures consistent testing

### API Strategy
- **Tavily**: Web search for company context
- **OpenAI/Anthropic**: Classification and email generation
- **Caching**: Store Tavily results to avoid duplicate calls

### Classification Rules
- Focus on Builders and Owners only
- Skip Competitors and Partners for emails
- Include confidence scores

### Email Generation
- Personalized based on category + role
- Emphasize booth #42 and free gift
- Professional tone, 3-4 sentences

## Session Notes

### Session 1 (Initial Setup)
- Created project structure
- Implemented all modules
- Set up documentation system

### Session 2 (Enhanced Parser Implementation)
- Discovered all 398 speakers have session data (472 total sessions)
- Found 60 speakers presenting at multiple sessions (15.1%)
- Extracted speaker image URLs from meta tags (100% coverage)
- Updated parser to capture sessions, images, and bio fields
- Enhanced email generator to reference speaker sessions
- Identified multi-session speakers as high-value targets