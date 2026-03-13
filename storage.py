"""
Storage Module for Lead Qualification Results
Supports Google Sheets and local CSV storage
"""
import csv
from typing import List, Dict, Any
from datetime import datetime
import config


def save_to_csv(results: List[Dict[str, Any]], filepath: str = None) -> str:
    """Save qualified leads to a CSV file"""
    if filepath is None:
        filepath = config.OUTPUT_CSV_PATH

    fieldnames = [
        'Name', 'Email', 'Company Name', 'Job Title', 'Message from Lead',
        'Lead Score', 'Priority', 'Industry', 'Business Need',
        'Recommended Action', 'Reasoning', 'Processed At'
    ]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return filepath


def save_to_google_sheets(results: List[Dict[str, Any]], sheet_name: str = None) -> str:
    """Save qualified leads to Google Sheets"""
    import gspread
    from google.oauth2.service_account import Credentials

    if sheet_name is None:
        sheet_name = config.GOOGLE_SHEET_NAME

    # Define scopes
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Authenticate
    credentials = Credentials.from_service_account_file(
        config.GOOGLE_SHEETS_CREDENTIALS_FILE,
        scopes=scopes
    )
    client = gspread.authorize(credentials)

    # Create or open spreadsheet
    try:
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.sheet1
        worksheet.clear()
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(sheet_name)
        worksheet = spreadsheet.sheet1
        # Share with anyone who has the link
        spreadsheet.share(None, perm_type='anyone', role='reader')

    # Prepare headers
    headers = [
        'Name', 'Email', 'Company Name', 'Job Title', 'Message from Lead',
        'Lead Score', 'Priority', 'Industry', 'Business Need',
        'Recommended Action', 'Reasoning', 'Processed At'
    ]

    # Prepare data rows
    rows = [headers]
    for result in results:
        row = [str(result.get(h, '')) for h in headers]
        rows.append(row)

    # Update sheet
    worksheet.update(rows, 'A1')

    # Format header row
    worksheet.format('A1:L1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.2, 'green': 0.5, 'blue': 0.8}
    })

    # Auto-resize columns
    worksheet.columns_auto_resize(0, 11)

    return spreadsheet.url


def load_leads_from_csv(filepath: str = None) -> List[Dict[str, str]]:
    """Load leads from CSV file"""
    if filepath is None:
        filepath = config.INPUT_CSV_PATH

    leads = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(dict(row))

    return leads


def format_result_for_storage(lead: Dict[str, str], analysis) -> Dict[str, Any]:
    """Format lead and analysis for storage"""
    return {
        'Name': lead.get('Name', ''),
        'Email': lead.get('Email', ''),
        'Company Name': lead.get('Company Name', ''),
        'Job Title': lead.get('Job Title', ''),
        'Message from Lead': lead.get('Message from Lead', ''),
        'Lead Score': analysis.lead_score,
        'Priority': analysis.priority,
        'Industry': analysis.industry,
        'Business Need': analysis.business_need,
        'Recommended Action': analysis.recommended_action,
        'Reasoning': analysis.reasoning,
        'Processed At': datetime.now().isoformat()
    }
