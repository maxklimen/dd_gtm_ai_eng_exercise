# DroneDeploy GTM Email Generation Pipeline

An AI-powered pipeline that generates personalized outbound emails for conference speakers, targeting potential DroneDeploy customers at Digital Construction Week.

> **For implementation details and results**: See [SUBMISSION_NOTES.md](SUBMISSION_NOTES.md)

## 🎯 Overview

This system processes conference speakers, enriches their company information, classifies them into customer categories, and generates personalized emails inviting potential customers to visit booth #42 for a demo and free gift.

**Key Features:**
- ⚡ Processes hundreds of speakers with parallel API calls
- 🔄 Resume capability with checkpoint system
- 🤖 Supports multiple LLMs (OpenAI GPT-4, Anthropic Claude)
- 📊 Intelligent company classification (Builder/Owner/Partner/Competitor/Customer)
- ✉️ Personalized email generation based on role and company type

## 📋 Requirements

- Python 3.8+
- API Keys (see Configuration section)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd dd_gtm_ai_eng_exercise
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file based on `.env_sample`:
```bash
cp .env_sample .env
```

Edit `.env` and add your API keys:
```env
# Web Search API
TAVILY_API_KEY=your_tavily_api_key

# LLM API (choose one)
OPENAI_API_KEY=your_openai_api_key
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 4. Run Pipeline
```bash
python main.py
```

The pipeline will:
1. Parse speaker data from pre-scraped HTML files
2. Enrich companies with web search data
3. Classify companies (Builder, Owner, Partner, Competitor, Customer)
4. Generate personalized emails for Builders and Owners
5. Export results to `out/email_list.csv`

## 📁 Project Structure

```
dd_gtm_ai_eng_exercise/
├── .env_sample         # API key template
├── main.py             # Main entry point
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── in/                 # Input data
│   └── scraped_pages/  # Pre-scraped speaker HTML files
├── out/                # Output directory
│   └── email_list.csv  # Final output (generated)
└── utils/              # Utility modules
    ├── parser.py       # HTML parsing
    ├── enrichment.py   # Company enrichment via Tavily
    ├── classifier.py   # LLM-based classification
    ├── email_generator.py  # Email content generation
    └── stage*.py       # Pipeline stages with checkpointing
```

## 📊 Output Format

The pipeline generates `out/email_list.csv` with the following columns:
- **Speaker Name**: Full name of the speaker
- **Speaker Title**: Job title/role
- **Speaker Company**: Company name
- **Company Category**: Classification (Builder/Owner/Partner/Competitor/Customer/Other)
- **Email Subject**: Personalized subject line
- **Email Body**: Personalized email content

## 🎨 Advanced Usage

### Run Specific Stages
```bash
# Classification only
python main.py --classify

# Email generation only
python main.py --generate

# Export to CSV only
python main.py --export
```

### Resume from Checkpoint
If the pipeline is interrupted, resume from the last checkpoint:
```bash
python main.py --classify --resume
```

## ⚡ Performance

The pipeline processes speakers in three stages with checkpointing:

1. **Classification Stage**: ~10-12 minutes for 400 speakers
2. **Email Generation Stage**: ~2-3 minutes for 100-150 emails  
3. **Export Stage**: <1 minute

**Total Runtime**: ~15-20 minutes for complete pipeline

### Resource Usage
- **API Costs**: ~$0.80 for 400 speakers
- **Memory**: <500MB
- **Network**: Moderate (API calls are rate-limited)

The pipeline includes checkpoint/resume capability to handle interruptions and can be run in stages for large datasets.

**Note**: For actual development timeline and lessons learned, see [SUBMISSION_NOTES.md](SUBMISSION_NOTES.md)

## 📊 Output Format

The pipeline generates `out/email_list.csv` with the following columns:
- **Speaker Name**: Full name of the speaker
- **Speaker Title**: Job title/role
- **Speaker Company**: Company name
- **Company Category**: Classification (Builder/Owner/Partner/Competitor/Customer/Other)
- **Email Subject**: Personalized subject line (empty for non-targets)
- **Email Body**: Personalized email content (empty for non-targets)

Only Builders and Owners receive personalized emails. Partners, Competitors, Customers, and Others are classified but excluded from outreach.

## 🏗️ Architecture

### Pipeline Stages

1. **Data Parsing**
   - Extracts speaker information from HTML files
   - Captures: name, title, company, sessions, bio

2. **Company Enrichment**
   - Uses Tavily API for web search
   - Caches results to avoid duplicate API calls
   - Gathers company context and industry information

3. **Classification**
   - Uses LLM to categorize companies:
     - **Builder**: Construction companies, contractors, engineering firms
     - **Owner**: Property owners, developers, government agencies
     - **Partner**: Software vendors, consultants (excluded from emails)
     - **Competitor**: Competing drone/tech companies (excluded)
     - **Customer**: Existing DroneDeploy customers (excluded)

4. **Email Generation**
   - Creates personalized emails for Builders and Owners only
   - References speaker's sessions and company context
   - Emphasizes booth #42 and free gift

5. **CSV Export**
   - Formats all data into required CSV structure
   - Sorts by category (Builders first)

### Reliability Features

- **Checkpoint System**: Saves progress every 10-25 speakers
- **Resume Capability**: Can continue from last checkpoint after failure
- **Error Handling**: Graceful failure with retry logic
- **Caching**: Reduces API calls and improves performance

## 🔧 Configuration

### API Selection
The system automatically detects which API key is provided:
- If `OPENAI_API_KEY` is set → Uses GPT-4.1-mini
- If `ANTHROPIC_API_KEY` is set → Uses Claude Sonnet 4

### Model Configuration
Models are configured in `utils/classifier.py` and `utils/email_generator.py`:
- OpenAI: `gpt-4.1-mini-2025-04-14`
- Anthropic: `claude-sonnet-4-20250514`

## 📈 Scalability

The system scales linearly:
- 100 speakers: ~3 minutes
- 398 speakers: ~12 minutes
- 1,000 speakers: ~30 minutes
- 5,000 speakers: ~2.5 hours

## 🐛 Troubleshooting

### API Key Issues
- Ensure `.env` file exists and contains valid API keys
- Check API key format and permissions

### Timeout Issues
- Use staged execution with `--classify`, `--generate` flags
- Leverage resume capability with `--resume` flag

### Memory Issues
- The pipeline processes in batches to manage memory
- Default batch sizes are optimized for standard systems

## 📝 Documentation

- **[SUBMISSION_NOTES.md](SUBMISSION_NOTES.md)** - Development timeline, lessons learned, and future improvements
- **[CLAUDE.md](CLAUDE.md)** - Project context and persistent memory for AI assistants

## 🐛 Known Issues

- Environment timeout constraints may require staged execution for very large datasets
- API rate limits are conservatively set (see [SUBMISSION_NOTES.md](SUBMISSION_NOTES.md) for optimization potential)

## 📝 License

This project was created as a technical exercise for DroneDeploy.

## 🤝 Support

For issues or questions, please check the code documentation or review the utility modules in the `utils/` directory.