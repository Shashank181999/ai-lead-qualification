"""
Configuration settings for AI Lead Qualification System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Choose which LLM to use: "openai", "anthropic", or "groq"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# Model settings
OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-3-haiku-20240307"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Lead Qualification Results")

# CSV Input/Output
INPUT_CSV_PATH = os.getenv("INPUT_CSV_PATH", "sample_leads.csv")
OUTPUT_CSV_PATH = os.getenv("OUTPUT_CSV_PATH", "qualified_leads.csv")

# Scoring thresholds
HIGH_PRIORITY_THRESHOLD = 70
MEDIUM_PRIORITY_THRESHOLD = 40
