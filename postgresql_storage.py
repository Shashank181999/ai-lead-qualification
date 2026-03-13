"""
PostgreSQL Storage Module (Supabase)
Save qualified leads to PostgreSQL cloud database
"""
import os
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Get DATABASE_URL from Streamlit secrets or environment"""
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except:
        pass
    return os.getenv("DATABASE_URL")

# Supabase PostgreSQL connection
DATABASE_URL = get_database_url()


def get_connection():
    """Get PostgreSQL database connection"""
    import psycopg2
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None


def init_postgresql_table():
    """Create the leads table if it doesn't exist"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qualified_leads (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                company_name VARCHAR(255),
                job_title VARCHAR(255),
                message TEXT,
                lead_score INTEGER,
                priority VARCHAR(50),
                industry VARCHAR(255),
                business_need TEXT,
                recommended_action TEXT,
                reasoning TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False


def save_leads_to_postgresql(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Save leads to PostgreSQL database"""
    conn = get_connection()
    if not conn:
        return {"success": False, "error": "Database not connected"}

    try:
        cursor = conn.cursor()
        count = 0

        for lead in leads:
            try:
                cursor.execute('''
                    INSERT INTO qualified_leads
                    (name, email, company_name, job_title, message, lead_score,
                     priority, industry, business_need, recommended_action, reasoning, processed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                        lead_score = EXCLUDED.lead_score,
                        priority = EXCLUDED.priority,
                        industry = EXCLUDED.industry,
                        business_need = EXCLUDED.business_need,
                        recommended_action = EXCLUDED.recommended_action,
                        processed_at = EXCLUDED.processed_at
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
                print(f"Error inserting lead: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        return {"success": True, "created_count": count}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_all_leads_from_postgresql() -> List[Dict[str, Any]]:
    """Get all leads from PostgreSQL"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, email, company_name, job_title, lead_score,
                   priority, industry, business_need, recommended_action, processed_at
            FROM qualified_leads
            ORDER BY lead_score DESC
        ''')

        columns = ['Name', 'Email', 'Company', 'Job Title', 'Lead Score',
                   'Priority', 'Industry', 'Business Need', 'Recommended Action', 'Processed At']

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        print(f"Error fetching leads: {e}")
        return []


def get_postgresql_stats() -> Dict[str, Any]:
    """Get stats from PostgreSQL database"""
    conn = get_connection()
    if not conn:
        return {}

    try:
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

        cursor.close()
        conn.close()

        return {
            'total_leads': total,
            'average_score': round(float(avg_score), 1),
            'high_priority': priority_counts.get('High', 0),
            'medium_priority': priority_counts.get('Medium', 0),
            'low_priority': priority_counts.get('Low', 0)
        }

    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}


def check_postgresql_connection() -> bool:
    """Check if PostgreSQL connection is working"""
    conn = get_connection()
    if conn:
        conn.close()
        return True
    return False


def clear_postgresql_leads():
    """Delete all leads from PostgreSQL"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM qualified_leads')
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing leads: {e}")
        return False
