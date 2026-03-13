# AI Lead Qualification System

An AI-powered web application that automatically analyzes and qualifies sales leads using LLM technology.

## Features

- **AI-Powered Analysis**: Uses Groq LLM (Llama 3.3 70B) to analyze leads
- **Lead Scoring**: Scores leads from 0-100 based on multiple factors
- **Priority Classification**: Categorizes leads as High/Medium/Low priority
- **Industry Detection**: Identifies the industry of each lead
- **Business Need Identification**: Extracts potential business needs from messages
- **Cloud Storage**: PostgreSQL database via Supabase
- **Local Storage**: SQLite backup for offline access
- **Export Options**: Download results as CSV or JSON
- **Mobile Responsive**: Works on desktop and mobile devices

## System Architecture

```
CSV Upload --> AI Analysis (Groq LLM) --> Lead Scoring --> Storage (PostgreSQL/SQLite)
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit (Python) |
| AI/LLM | Groq API (Llama 3.3 70B) |
| Cloud Database | PostgreSQL (Supabase) |
| Local Database | SQLite |

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-lead-qualification.git
cd ai-lead-qualification
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# LLM Provider
LLM_PROVIDER=groq

# Groq API Key (FREE - get from https://console.groq.com)
GROQ_API_KEY=your_groq_api_key_here

# PostgreSQL Connection (FREE - get from https://supabase.com)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres
```

### 4. Get API Keys

**Groq API (FREE)**:
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Create API key
4. Copy to `.env` file

**Supabase PostgreSQL (FREE)**:
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Go to **Connect** > **Connection string** > **URI**
4. Select **Session Pooler** mode
5. Copy connection string to `.env` file

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## How to Use

1. **Upload CSV**: Click "Browse files" and upload your leads CSV
2. **Analyze**: Click "Analyze Leads" button
3. **View Results**: See scored leads in card format
4. **Save to Cloud**: Go to PostgreSQL tab and click "Save to PostgreSQL"
5. **Download**: Export results as CSV or JSON

## Input CSV Format

Your CSV file should have these columns:

| Column | Description |
|--------|-------------|
| Name | Lead's full name |
| Email | Lead's email address |
| Company Name | Company/Organization name |
| Job Title | Lead's position |
| Message from Lead | Their inquiry message |

**Example:**
```csv
Name,Email,Company Name,Job Title,Message from Lead
Rahul Sharma,rahul@techindia.com,TechIndia Solutions,CEO,Looking for AI automation tools for our sales team. Budget approved for Q2.
Priya Patel,priya@startupx.io,StartupX,Founder,Just raised Series A. Need CRM automation urgently.
```

## Lead Scoring System

The AI analyzes each lead and assigns a score based on:

| Score Range | Priority | Description |
|-------------|----------|-------------|
| 80-100 | High | Hot lead - Decision maker, clear budget, immediate need |
| 60-79 | Medium | Warm lead - Good fit, worth pursuing |
| 40-59 | Medium | Moderate lead - Needs nurturing |
| 0-39 | Low | Cold/Invalid - Low priority or spam |

### Scoring Factors

The AI considers these factors when scoring:

1. **Job Title Seniority**: CEO, VP, Director = higher score
2. **Company Size Indicators**: Large companies score higher
3. **Message Clarity**: Specific needs = higher score
4. **Budget Indicators**: Mentions of budget/funding increase score
5. **Urgency Signals**: Words like "urgent", "immediately" increase score
6. **Industry Fit**: Relevant industries score higher

## Project Structure

```
project/
├── app.py                 # Main Streamlit web interface
├── lead_analyzer.py       # AI analysis module (Groq integration)
├── config.py              # Configuration settings
├── storage.py             # Data formatting utilities
├── database.py            # SQLite local storage
├── postgresql_storage.py  # PostgreSQL/Supabase integration
├── requirements.txt       # Python dependencies
├── sample_leads.csv       # Sample input data
├── .env                   # Environment variables (not in git)
└── README.md              # This file
```

## How AI Analysis Works

1. **Input Processing**: Each lead's data is formatted into a structured prompt
2. **LLM Analysis**: Groq's Llama 3.3 70B model analyzes the lead
3. **Scoring**: AI returns JSON with score, industry, business need, and recommended action
4. **Priority Assignment**: Score is mapped to priority (High/Medium/Low)
5. **Storage**: Results saved to PostgreSQL and local SQLite

### Sample AI Prompt

```
Lead Information:
- Name: Rahul Sharma
- Email: rahul@techindia.com
- Company: TechIndia Solutions
- Job Title: CEO
- Message: Looking for AI automation tools...

Analyze and provide:
- lead_score (0-100)
- industry
- business_need
- recommended_action
```

## Troubleshooting

**PostgreSQL Connection Error**:
- Use Session Pooler URL (not Direct Connection)
- Verify password in connection string
- Check if Supabase project is active

**Groq API Error**:
- Verify API key is correct
- Check rate limits (free tier: 30 requests/minute)
- Ensure model name is correct: `llama-3.3-70b-versatile`

**App Not Loading**:
```bash
# Kill existing streamlit processes
pkill -f streamlit

# Restart
streamlit run app.py
```

## API Costs

| Provider | Model | Cost |
|----------|-------|------|
| Groq | Llama 3.3 70B | FREE |
| Supabase | PostgreSQL | FREE (up to 500MB) |

## License

MIT License
