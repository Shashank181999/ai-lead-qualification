# AI Lead Qualification Automation System

An AI-powered automation system that analyzes and qualifies sales leads automatically using LLM technology. The system processes leads from CSV files, generates intelligent lead scores, categorizes industries, identifies business needs, and provides actionable recommendations for the sales team.

## Features

- **AI-Powered Analysis**: Uses OpenAI, Anthropic Claude, or Groq LLMs to analyze leads
- **Intelligent Scoring**: Generates lead scores (0-100) based on multiple factors
- **Industry Classification**: Automatically categorizes leads by industry
- **Business Need Identification**: Extracts potential business needs from lead messages
- **Actionable Recommendations**: Provides specific next steps for sales team
- **Multiple Storage Options**: Save results to CSV or Google Sheets
- **Flexible LLM Support**: Works with OpenAI, Anthropic, or Groq APIs

## System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│  CSV Input  │ ──► │  AI Analysis │ ──► │Lead Scoring │ ──► │   Storage   │
│   (Leads)   │     │    (LLM)     │     │ & Priority  │     │ (CSV/Sheets)│
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
```

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd project
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use any text editor
```

### 4. Run the System

```bash
# Process the sample leads
python main.py

# Process with verbose output
python main.py -v

# Use a custom input file
python main.py -i your_leads.csv

# Save to both CSV and Google Sheets
python main.py -g
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LLM_PROVIDER` | LLM to use: `openai`, `anthropic`, or `groq` | Yes |
| `OPENAI_API_KEY` | OpenAI API key | If using OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | If using Anthropic |
| `GROQ_API_KEY` | Groq API key | If using Groq |
| `GOOGLE_SHEETS_CREDENTIALS_FILE` | Path to Google service account JSON | For Sheets |
| `INPUT_CSV_PATH` | Default input CSV file | No |
| `OUTPUT_CSV_PATH` | Default output CSV file | No |

### Input CSV Format

Your input CSV should have these columns:

| Column | Description |
|--------|-------------|
| Name | Lead's full name |
| Email | Lead's email address |
| Company Name | Name of the company |
| Job Title | Lead's job title/position |
| Message from Lead | The message or inquiry from the lead |

Example:
```csv
Name,Email,Company Name,Job Title,Message from Lead
Sarah Johnson,sarah@brighttech.io,BrightTech,VP of Operations,"Looking for automation tools..."
```

## Output

### Lead Score Interpretation

| Score Range | Priority | Description |
|-------------|----------|-------------|
| 80-100 | High | Hot lead - Decision maker, clear budget, immediate need |
| 60-79 | High | Warm lead - Good fit, buying signals present |
| 40-59 | Medium | Moderate lead - Potential fit, needs nurturing |
| 20-39 | Low | Cool lead - Low priority, unclear fit |
| 0-19 | Low | Cold/Invalid - Spam or no business potential |

### Example Output

```
──────────────────────────────────────────────────
Lead Name: Sarah Johnson
Company: BrightTech Solutions
Industry: SaaS / Technology
Lead Score: 78
Priority: High
Business Need: Automation tools for internal operations
Recommended Action: Schedule a demo call with the sales team
──────────────────────────────────────────────────
```

## Google Sheets Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account and download credentials JSON
5. Save as `credentials.json` in the project directory
6. Share the Google Sheet with the service account email

## Project Structure

```
project/
├── main.py              # Main entry point and workflow orchestration
├── lead_analyzer.py     # AI analysis module with LLM integration
├── storage.py           # Storage handlers (CSV, Google Sheets)
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── sample_leads.csv     # Sample input data (25 leads)
├── .env.example         # Environment template
└── README.md            # This file
```

## CLI Options

```
usage: main.py [-h] [-i INPUT] [-o OUTPUT] [-g] [-v] [--provider {openai,anthropic,groq}]

AI-powered Lead Qualification Automation System

options:
  -h, --help            show this help message and exit
  -i, --input           Input CSV file with leads (default: sample_leads.csv)
  -o, --output          Output CSV file for results (default: qualified_leads.csv)
  -g, --google-sheets   Also save results to Google Sheets
  -v, --verbose         Print detailed output for each lead
  --provider            Override LLM provider (openai, anthropic, groq)
```

## API Costs

Estimated costs per lead analysis:

| Provider | Model | Cost per Lead |
|----------|-------|---------------|
| OpenAI | gpt-4o-mini | ~$0.001 |
| Anthropic | claude-3-haiku | ~$0.001 |
| Groq | llama-3.1-70b | Free (rate limited) |

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your API key is correctly set in `.env`
2. **Module Not Found**: Run `pip install -r requirements.txt`
3. **Google Sheets Error**: Check service account permissions and credentials file
4. **Rate Limiting**: Add delays between API calls if processing many leads

### Debug Mode

```bash
# Run with verbose output to see detailed analysis
python main.py -v
```

## License

MIT License

## Author

Built for AI Lead Qualification Assessment
