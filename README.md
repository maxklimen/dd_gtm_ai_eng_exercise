# DroneDeploy GTM Email Generation Pipeline

An AI-powered pipeline that generates personalized outbound emails for conference speakers, targeting potential DroneDeploy customers at Digital Construction Week.

## 🎯 Overview

This system processes 398 conference speakers, enriches their company information, classifies them into customer categories, and generates personalized emails inviting them to visit booth #42 for a demo and free gift.

**Key Features:**
- ⚡ Processes 398 speakers in ~12 minutes
- 🔄 Resume capability with checkpoint system
- 🤖 Supports multiple LLMs (OpenAI GPT-4.1, Anthropic Claude)
- 📊 Intelligent company classification
- ✉️ Personalized email generation

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

## ⚡ Performance & Results

### Final Results (COMPLETE)
- **Total Speakers Processed**: 398 speakers (ALL speakers from conference)
- **Emails Generated**: 118 personalized emails
  - 95 for Builders (general contractors, construction companies) - 100% coverage
  - 23 for Owners (property developers, government agencies) - 100% coverage
- **Classifications**:
  - Partner: 159 (software/consulting - excluded from emails)
  - Other: 106 (non-construction industry - excluded)
  - Builder: 95 (ALL received emails)
  - Owner: 23 (ALL received emails)
  - Customer: 10 (existing DroneDeploy customers - excluded)
  - Competitor: 5 (competing solutions - excluded)

### Performance Metrics
With GPT-4.1-mini (recommended):
- **Total Time**: ~15-20 minutes for full pipeline
- **Enrichment**: 1.2 min (5.5 speakers/sec with caching)
- **Classification**: 10-12 min (batch processing with checkpoints)
- **Email Generation**: 2-3 min (98 emails total)
- **Cost**: ~$0.80 total

**Note**: Pipeline uses checkpoint/resume system to handle environment timeouts. Run in stages if processing large batches.

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

## 🚧 Current Limitations & Future Improvements

### Recent Fixes
- ✅ **Fixed deduplication bug in stage1_classify.py** (lines 40-43, 56-58, 100-101)
  - **Problem**: Was tracking by company only, skipping speakers from same company
  - **Impact**: Only 315 of 398 speakers were processed
  - **Solution**: Now tracks unique speaker IDs (name + company)
  - **Result**: All 398 speakers properly processed

### Current Limitations
- Environment timeout constraints require staged execution
- Could be 40x faster with proper parallelization (currently using ~2% of API capacity)

### Future Improvements
- Enhanced parallelization for faster processing
- Better prompt engineering for more accurate classifications
- Deduplication logic for speakers with multiple sessions
- Real-time progress dashboard
- A/B testing framework for email templates
- Integration with CRM systems for automated outreach

## 📝 License

This project was created as a technical exercise for DroneDeploy.

## 🤝 Support

For issues or questions, please check the code documentation or review the utility modules in the `utils/` directory.