"""
Database Storage Module
SQLite database for storing qualified leads
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import os

DATABASE_FILE = "leads_database.db"


def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qualified_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            company_name TEXT,
            job_title TEXT,
            message TEXT,
            lead_score INTEGER,
            priority TEXT,
            industry TEXT,
            business_need TEXT,
            recommended_action TEXT,
            reasoning TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_lead_score ON qualified_leads(lead_score DESC)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_priority ON qualified_leads(priority)
    ''')

    conn.commit()
    conn.close()


def save_lead_to_db(lead_data: Dict[str, Any]) -> int:
    """Save a single qualified lead to database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR REPLACE INTO qualified_leads
            (name, email, company_name, job_title, message, lead_score,
             priority, industry, business_need, recommended_action, reasoning, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead_data.get('Name', ''),
            lead_data.get('Email', ''),
            lead_data.get('Company Name', ''),
            lead_data.get('Job Title', ''),
            lead_data.get('Message from Lead', ''),
            lead_data.get('Lead Score', 0),
            lead_data.get('Priority', 'Low'),
            lead_data.get('Industry', ''),
            lead_data.get('Business Need', ''),
            lead_data.get('Recommended Action', ''),
            lead_data.get('Reasoning', ''),
            lead_data.get('Processed At', datetime.now().isoformat())
        ))

        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def save_leads_batch(leads: List[Dict[str, Any]]) -> int:
    """Save multiple leads to database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    count = 0
    for lead in leads:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO qualified_leads
                (name, email, company_name, job_title, message, lead_score,
                 priority, industry, business_need, recommended_action, reasoning, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead.get('Name', ''),
                lead.get('Email', ''),
                lead.get('Company Name', ''),
                lead.get('Job Title', ''),
                lead.get('Message from Lead', ''),
                lead.get('Lead Score', 0),
                lead.get('Priority', 'Low'),
                lead.get('Industry', ''),
                lead.get('Business Need', ''),
                lead.get('Recommended Action', ''),
                lead.get('Reasoning', ''),
                lead.get('Processed At', datetime.now().isoformat())
            ))
            count += 1
        except Exception as e:
            print(f"Error saving lead: {e}")

    conn.commit()
    conn.close()
    return count


def get_all_leads() -> List[Dict[str, Any]]:
    """Retrieve all leads from database"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM qualified_leads ORDER BY lead_score DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_leads_by_priority(priority: str) -> List[Dict[str, Any]]:
    """Get leads filtered by priority"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM qualified_leads WHERE priority = ? ORDER BY lead_score DESC
    ''', (priority,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_lead_stats() -> Dict[str, Any]:
    """Get statistics about stored leads"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Total count
    cursor.execute('SELECT COUNT(*) FROM qualified_leads')
    total = cursor.fetchone()[0]

    # Average score
    cursor.execute('SELECT AVG(lead_score) FROM qualified_leads')
    avg_score = cursor.fetchone()[0] or 0

    # Priority counts
    cursor.execute('''
        SELECT priority, COUNT(*) FROM qualified_leads GROUP BY priority
    ''')
    priority_counts = dict(cursor.fetchall())

    # Industry breakdown
    cursor.execute('''
        SELECT industry, COUNT(*) FROM qualified_leads GROUP BY industry ORDER BY COUNT(*) DESC LIMIT 10
    ''')
    industry_counts = dict(cursor.fetchall())

    conn.close()

    return {
        'total_leads': total,
        'average_score': round(avg_score, 1),
        'high_priority': priority_counts.get('High', 0),
        'medium_priority': priority_counts.get('Medium', 0),
        'low_priority': priority_counts.get('Low', 0),
        'industries': industry_counts
    }


def delete_all_leads():
    """Clear all leads from database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM qualified_leads')
    conn.commit()
    conn.close()


def search_leads(query: str) -> List[Dict[str, Any]]:
    """Search leads by name, company, or email"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    search_term = f"%{query}%"
    cursor.execute('''
        SELECT * FROM qualified_leads
        WHERE name LIKE ? OR company_name LIKE ? OR email LIKE ?
        ORDER BY lead_score DESC
    ''', (search_term, search_term, search_term))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# Initialize database on module import
init_database()
