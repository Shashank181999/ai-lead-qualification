#!/usr/bin/env python3
"""
AI Lead Qualification System - Web Interface
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Cache imports for faster loading
@st.cache_resource
def load_modules():
    from lead_analyzer import analyze_lead
    from storage import format_result_for_storage
    from database import save_leads_batch, get_all_leads, get_lead_stats, delete_all_leads
    from postgresql_storage import (
        save_leads_to_postgresql, get_all_leads_from_postgresql,
        get_postgresql_stats, check_postgresql_connection, init_postgresql_table
    )
    return (analyze_lead, format_result_for_storage, save_leads_batch,
            get_all_leads, get_lead_stats, delete_all_leads,
            save_leads_to_postgresql, get_all_leads_from_postgresql,
            get_postgresql_stats, check_postgresql_connection, init_postgresql_table)

(analyze_lead, format_result_for_storage, save_leads_batch,
 get_all_leads, get_lead_stats, delete_all_leads,
 save_leads_to_postgresql, get_all_leads_from_postgresql,
 get_postgresql_stats, check_postgresql_connection, init_postgresql_table) = load_modules()

# Cache connection check (TTL = 60 seconds)
@st.cache_data(ttl=60)
def cached_pg_check():
    return check_postgresql_connection()

@st.cache_data(ttl=30)
def cached_db_stats():
    return get_lead_stats()

@st.cache_data(ttl=30)
def cached_pg_stats():
    return get_postgresql_stats()

# Page configuration
st.set_page_config(
    page_title="AI Lead Qualification System",
    page_icon="🎯",
    layout="wide",
    menu_items={}
)

# Simple CSS - Black and White theme
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stApp > header {display: none !important;}

    /* Simple header */
    .main-header {
        background: #111;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #333;
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        color: white;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        color: #aaa;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #1a1a1a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #333;
    }

    /* Desktop/Mobile view switching */
    .desktop-only { display: block; }
    .mobile-only { display: none; }

    /* Mobile responsive */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] { display: none !important; }

        .main .block-container { padding: 1rem; }

        h1, h2, h3 { font-size: 1.2rem !important; }

        .stTabs [data-baseweb="tab"] {
            font-size: 0.7rem !important;
            padding: 8px 12px !important;
        }

        .desktop-only { display: none !important; }
        .mobile-only { display: block !important; }

        /* 2x2 grid for metrics */
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 8px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header with gradient
st.markdown("""
<div class="main-header">
    <h1>AI Lead Qualification System</h1>
    <p>Automatically analyze and score your sales leads using AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    This system analyzes leads and provides:
    - **Lead Score** (0-100)
    - **Industry** classification
    - **Business Need** identification
    - **Recommended Action** for sales team
    """)

    st.divider()

    st.markdown("### Scoring Guide")
    st.markdown("""
    - **80-100**: Hot Lead
    - **60-79**: Warm Lead
    - **40-59**: Moderate Lead
    - **0-39**: Cold/Invalid
    """)


# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Upload Leads")
    uploaded_file = st.file_uploader(
        "Upload your CSV file with leads",
        type=['csv'],
        help="CSV should have columns: Name, Email, Company Name, Job Title, Message from Lead"
    )

with col2:
    st.header("Required Columns")
    st.code("""
Name
Email
Company Name
Job Title
Message from Lead
    """)

# Process leads
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded {len(df)} leads from uploaded file")

    with st.expander("Preview Input Data", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)

    if st.button("Analyze Leads", type="primary", use_container_width=True):

        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, row in df.iterrows():
            if pd.isna(row.get('Name')) or pd.isna(row.get('Email')):
                continue

            progress = (idx + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"Analyzing: {row.get('Name', 'Unknown')}...")

            lead = row.to_dict()
            analysis = analyze_lead(lead)
            result = format_result_for_storage(lead, analysis)
            results.append(result)

        progress_bar.empty()
        status_text.empty()

        results_df = pd.DataFrame(results)
        st.session_state['results'] = results_df

        # Save to local database
        saved_count = save_leads_batch(results)
        st.success(f"Successfully analyzed {len(results)} leads and saved to database!")

# Display results
if 'results' in st.session_state:
    results_df = st.session_state['results']

    st.divider()
    st.header("Results")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Leads", len(results_df))
    with col2:
        avg_score = results_df['Lead Score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}")
    with col3:
        high_priority = len(results_df[results_df['Priority'] == 'High'])
        st.metric("High Priority", high_priority, delta=f"{high_priority/len(results_df)*100:.0f}%")
    with col4:
        low_priority = len(results_df[results_df['Priority'] == 'Low'])
        st.metric("Low Priority", low_priority)

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["All Leads", "High Priority", "Analytics", "PostgreSQL", "Local DB"])

    with tab1:
        # Short action keywords
        def short_action(action):
            action = str(action).lower()
            if 'ignore' in action or 'not pursue' in action:
                return 'Ignore'
            elif 'demo' in action:
                return 'Schedule Demo'
            elif 'call' in action:
                return 'Call'
            elif 'email' in action or 'send' in action:
                return 'Send Email'
            elif 'proposal' in action:
                return 'Send Proposal'
            else:
                return 'Follow Up'

        display_df = results_df.copy()
        display_df['Action'] = display_df['Recommended Action'].apply(short_action)
        sorted_df = display_df.sort_values('Lead Score', ascending=False)

        # Desktop: Table view
        display_cols = ['Name', 'Company Name', 'Lead Score', 'Priority', 'Industry', 'Action']
        st.markdown('<div class="desktop-only">', unsafe_allow_html=True)
        st.dataframe(
            sorted_df[display_cols],
            use_container_width=True,
            height=400
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Mobile: Card view
        st.markdown('<div class="mobile-only">', unsafe_allow_html=True)
        for _, row in sorted_df.iterrows():
            st.markdown(f"""
            <div style="background: #1e1e1e; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {'#22c55e' if row['Priority']=='High' else '#eab308' if row['Priority']=='Medium' else '#ef4444'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 1rem;">{row['Name']}</strong>
                    <span style="background: {'#22c55e' if row['Priority']=='High' else '#eab308' if row['Priority']=='Medium' else '#ef4444'}; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">{row['Lead Score']}</span>
                </div>
                <div style="color: #aaa; font-size: 0.85rem; margin-top: 4px;">{row['Company Name']}</div>
                <div style="display: flex; gap: 10px; margin-top: 8px; flex-wrap: wrap;">
                    <span style="font-size: 0.75rem; background: #333; padding: 2px 6px; border-radius: 4px;">{row['Industry']}</span>
                    <span style="font-size: 0.75rem; background: #333; padding: 2px 6px; border-radius: 4px;">{row['Priority']}</span>
                    <span style="font-size: 0.75rem; background: #2563eb; padding: 2px 6px; border-radius: 4px;">{row['Action']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        high_df = results_df[results_df['Priority'] == 'High'].copy()
        high_df['Action'] = high_df['Recommended Action'].apply(short_action)
        sorted_high = high_df.sort_values('Lead Score', ascending=False)

        if len(sorted_high) == 0:
            st.info("No high priority leads found")
        else:
            # Desktop: Table view
            display_cols = ['Name', 'Company Name', 'Lead Score', 'Priority', 'Industry', 'Action']
            st.markdown('<div class="desktop-only">', unsafe_allow_html=True)
            st.dataframe(
                sorted_high[display_cols],
                use_container_width=True,
                height=400
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # Mobile: Card view
            st.markdown('<div class="mobile-only">', unsafe_allow_html=True)
            for _, row in sorted_high.iterrows():
                st.markdown(f"""
                <div style="background: #1e1e1e; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #22c55e;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 1rem;">{row['Name']}</strong>
                        <span style="background: #22c55e; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem;">{row['Lead Score']}</span>
                    </div>
                    <div style="color: #aaa; font-size: 0.85rem; margin-top: 4px;">{row['Company Name']}</div>
                    <div style="display: flex; gap: 10px; margin-top: 8px; flex-wrap: wrap;">
                        <span style="font-size: 0.75rem; background: #333; padding: 2px 6px; border-radius: 4px;">{row['Industry']}</span>
                        <span style="font-size: 0.75rem; background: #2563eb; padding: 2px 6px; border-radius: 4px;">{row['Action']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Lead Score Distribution")
            score_data = results_df['Lead Score'].value_counts().sort_index()
            st.bar_chart(score_data)

        with col2:
            st.subheader("Industry Breakdown")
            industry_data = results_df['Industry'].value_counts()
            st.bar_chart(industry_data)

        st.subheader("Priority Distribution")
        priority_counts = results_df['Priority'].value_counts()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("High", priority_counts.get('High', 0))
        with col2:
            st.metric("Medium", priority_counts.get('Medium', 0))
        with col3:
            st.metric("Low", priority_counts.get('Low', 0))

    with tab4:
        st.subheader("PostgreSQL Cloud Storage (Supabase)")

        pg_connected = check_postgresql_connection()

        if pg_connected:
            st.success("Connected to PostgreSQL")

            init_postgresql_table()

            if st.button("Save to PostgreSQL", type="primary"):
                result = save_leads_to_postgresql(results_df.to_dict('records'))
                if result['success']:
                    st.success(f"Saved {result['created_count']} leads to PostgreSQL!")
                else:
                    st.error(f"Error: {result.get('error')}")

            st.divider()

            pg_stats = get_postgresql_stats()
            if pg_stats:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total in DB", pg_stats.get('total_leads', 0))
                with col2:
                    st.metric("Avg Score", pg_stats.get('average_score', 0))
                with col3:
                    st.metric("High Priority", pg_stats.get('high_priority', 0))
                with col4:
                    st.metric("Low Priority", pg_stats.get('low_priority', 0))

            st.subheader("Leads in PostgreSQL")
            pg_leads = get_all_leads_from_postgresql()
            if pg_leads:
                pg_df = pd.DataFrame(pg_leads)
                st.dataframe(pg_df, use_container_width=True, height=300)
            else:
                st.info("No leads in PostgreSQL yet. Click 'Save to PostgreSQL' to upload.")

        else:
            st.warning("PostgreSQL not configured")
            st.markdown("""
            **To enable PostgreSQL storage (FREE with Supabase):**

            1. Go to [supabase.com](https://supabase.com) → Sign up free
            2. Create a new project
            3. Go to **Connect** → Copy **Connection string (URI)**
            4. Add to your `.env` file:
            ```
            DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
            ```
            5. Restart the app
            """)

    with tab5:
        st.subheader("Local Database Storage")
        st.info("All analyzed leads are automatically saved to local SQLite database")

        db_stats = get_lead_stats()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total in DB", db_stats['total_leads'])
        with col2:
            st.metric("Avg Score", db_stats['average_score'])
        with col3:
            st.metric("High Priority", db_stats['high_priority'])
        with col4:
            st.metric("Low Priority", db_stats['low_priority'])

        st.divider()

        st.subheader("All Stored Leads")
        db_leads = get_all_leads()
        if db_leads:
            db_df = pd.DataFrame(db_leads)
            display_cols_db = ['name', 'company_name', 'lead_score', 'priority', 'industry', 'business_need', 'processed_at']
            st.dataframe(
                db_df[display_cols_db].sort_values('lead_score', ascending=False),
                use_container_width=True,
                height=300
            )
        else:
            st.warning("No leads in database yet")

        st.divider()
        if st.button("Clear Database", type="secondary"):
            delete_all_leads()
            st.success("Database cleared!")
            st.rerun()

    # Download section
    st.divider()
    st.header("Download Results")

    col1, col2 = st.columns(2)

    with col1:
        csv_buffer = io.StringIO()
        results_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"qualified_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        json_data = results_df.to_json(orient='records', indent=2)

        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"qualified_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>AI Lead Qualification System</p>
</div>
""", unsafe_allow_html=True)
