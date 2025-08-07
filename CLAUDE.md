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

### ✅ FINAL RESULTS (4 hours total)
- **398 speakers processed** (ALL speakers from HTML files)
- **118 personalized emails generated**:
  - 95 for Builders (100% coverage)
  - 23 for Owners (100% coverage)
- **270 unique companies** identified
- **Categories**:
  - Partner: 159 (excluded from emails)
  - Other: 106 (excluded from emails)
  - Builder: 95 (ALL with emails)
  - Owner: 23 (ALL with emails)
  - Customer: 10 (existing DroneDeploy users - excluded)
  - Competitor: 5 (excluded)

### Timeline Breakdown
- **30 min**: Initial structure & core implementation
- **1.5 hours**: Testing, API integration, running pipeline
- **2 hours**: Debugging company deduplication bug
- **30 min**: Final optimization & documentation

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

### Session 3 (Full Pipeline & Bug Fixes - 4 hours)
- **Critical Bug Found**: Stage1 classifier was deduplicating by company, not speaker
  - Impact: Only 315 of 398 speakers processed
  - Fix: Track speakers by name+company ID
- **Performance Analysis**: Current pipeline uses only ~2% of API rate limits
  - Could achieve 40x speedup with proper parallelization
  - Designed optimized architecture (not implemented due to time)
- **Final Achievement**: ALL 398 speakers processed, 118 emails generated

## Key Lessons Learned

1. **Planning is Critical**: Spending more time upfront on orchestration design would have avoided the deduplication bug
2. **Calculate API Limits First**: We were using 1 req/sec when we could use 80 req/sec
3. **Test Data Flow Early**: The bug would have been caught with proper testing of intermediate results
4. **Checkpoint Systems Essential**: Saved us from losing work during timeouts
5. **Cache Everything**: Tavily cache saved significant API costs during debugging