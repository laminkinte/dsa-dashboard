"""
DSA Performance Dashboard - Complete Streamlit Application
Author: DSA Analytics Team
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add utils to path for Streamlit Cloud
sys.path.append(os.path.dirname(__file__))

# Import custom modules
try:
    from utils.analyzer import DSA_Analyzer
    from utils.helpers import (
        format_number, 
        validate_file, 
        create_excel_download,
        filter_by_dsa
    )
except ImportError as e:
    st.error(f"❌ Import Error: {str(e)}")
    st.info("Please ensure the 'utils' directory exists with all required modules.")

warnings.filterwarnings('ignore')

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="DSA Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/dsa-dashboard',
        'Report a bug': 'https://github.com/yourusername/dsa-dashboard/issues',
        'About': """
        # DSA Performance Dashboard v1.0.0
        
        Comprehensive analytics platform for DSA performance tracking.
        
        **Features:**
        - Upload and analyze multiple data sources
        - Filter by DSA IDs and date ranges
        - Generate interactive reports
        - Download results in Excel/CSV format
        - Visualize performance metrics
        
        **Contact:** support@dsa-analytics.com
        """
    }
)

# ================================
# CUSTOM CSS (Optimized for Cloud)
# ================================
st.markdown("""
<style>
    /* Professional styling */
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #374151;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3B82F6;
        transition: transform 0.3s ease;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
    }
    
    .sidebar-title {
        color: white !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        padding-top: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #10B981, #34D399);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #059669, #10B981);
        transform: scale(1.02);
    }
    
    .download-button {
        background: linear-gradient(90deg, #8B5CF6, #A78BFA) !important;
    }
    
    /* Data table styling */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        font-size: 14px;
    }
    
    .dataframe th {
        background: #3B82F6;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        position: sticky;
        top: 0;
    }
    
    .dataframe td {
        padding: 10px;
        border-bottom: 1px solid #E5E7EB;
    }
    
    .dataframe tr:hover {
        background-color: #F3F4F6;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #F3F4F6;
        padding: 4px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6;
        color: white;
    }
    
    /* Status indicators */
    .success-box {
        background: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #DBEAFE;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3B82F6, #8B5CF6);
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        border: 2px dashed #3B82F6;
        border-radius: 8px;
        padding: 20px;
        background: rgba(59, 130, 246, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# ================================
# SESSION STATE MANAGEMENT
# ================================
def initialize_session_state():
    """Initialize session state variables"""
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = DSA_Analyzer()
    if 'report1_data' not in st.session_state:
        st.session_state.report1_data = None
    if 'report2_data' not in st.session_state:
        st.session_state.report2_data = None
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'current_report' not in st.session_state:
        st.session_state.current_report = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}

# ================================
# DISPLAY FUNCTIONS FOR REPORT 1
# ================================
def display_report1_metrics(report_data, dsa_filter):
    """Display metrics for Report 1"""
    dsa_summary = report_data.get('dsa_summary', pd.DataFrame())
    qualified_df = report_data.get('qualified_customers', pd.DataFrame())
    
    # Apply DSA filter
    if dsa_filter and not dsa_summary.empty:
        dsas = [d.strip() for d in dsa_filter.split(',') if d.strip()]
        if dsas:
            dsa_summary = dsa_summary[dsa_summary['dsa_mobile'].isin(dsas)]
            qualified_df = filter_by_dsa(qualified_df, dsa_filter)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_dsas = dsa_summary['dsa_mobile'].nunique() if not dsa_summary.empty else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total DSAs</div>
            <div class='metric-value'>{format_number(total_dsas)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_customers = dsa_summary['Customer_Count'].sum() if not dsa_summary.empty else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Customers</div>
            <div class='metric-value'>{format_number(total_customers)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        qualified_count = len(qualified_df[qualified_df['customer_mobile'] != '']) if not qualified_df.empty else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Qualified Customers</div>
            <div class='metric-value'>{format_number(qualified_count)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_payment = (dsa_summary['Customer_Count'] * 40).sum() if not dsa_summary.empty else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Payment</div>
            <div class='metric-value'>${format_number(total_payment)}</div>
        </div>
        """, unsafe_allow_html=True)

def display_report1_details(report_data, dsa_filter):
    """Display detailed data for Report 1"""
    tab1, tab2, tab3 = st.tabs(["📋 Qualified Customers", "📊 DSA Summary", "📈 Visualizations"])
    
    with tab1:
        qualified_df = report_data.get('qualified_customers', pd.DataFrame())
        
        if dsa_filter and not qualified_df.empty:
            qualified_df = filter_by_dsa(qualified_df, dsa_filter)
        
        if not qualified_df.empty:
            st.dataframe(
                qualified_df,
                use_container_width=True,
                height=500,
                column_config={
                    "ticket_amount": st.column_config.NumberColumn("Ticket Amount", format="$%.2f"),
                    "scan_amount": st.column_config.NumberColumn("Scan Amount", format="$%.2f"),
                    "Payment (Customer Count *40)": st.column_config.NumberColumn("Payment", format="$%.0f"),
                }
            )
        else:
            st.warning("No qualified customers found in the data.")
    
    with tab2:
        dsa_summary = report_data.get('dsa_summary', pd.DataFrame())
        
        if dsa_filter and not dsa_summary.empty:
            dsas = [d.strip() for d in dsa_filter.split(',') if d.strip()]
            if dsas:
                dsa_summary = dsa_summary[dsa_summary['dsa_mobile'].isin(dsas)]
        
        if not dsa_summary.empty:
            st.dataframe(
                dsa_summary,
                use_container_width=True,
                height=500,
                column_config={
                    "Ticket_Conversion_Rate": st.column_config.NumberColumn("Ticket Conv %", format="%.1f%%"),
                    "Scan_Conversion_Rate": st.column_config.NumberColumn("Scan Conv %", format="%.1f%%"),
                    "Deposit_Conversion_Rate": st.column_config.NumberColumn("Deposit Conv %", format="%.1f%%"),
                    "Total_Ticket_Amount": st.column_config.NumberColumn("Total Ticket", format="$%.2f"),
                    "Total_Scan_Amount": st.column_config.NumberColumn("Total Scan", format="$%.2f"),
                }
            )
        else:
            st.warning("No DSA summary data available.")
    
    with tab3:
        dsa_summary = report_data.get('dsa_summary', pd.DataFrame())
        
        if not dsa_summary.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top 10 DSAs by customer count
                top10 = dsa_summary.sort_values('Customer_Count', ascending=False).head(10)
                if not top10.empty:
                    fig1 = px.bar(
                        top10,
                        x='dsa_mobile',
                        y='Customer_Count',
                        title='Top 10 DSAs by Customer Count',
                        labels={'dsa_mobile': 'DSA Mobile', 'Customer_Count': 'Customer Count'},
                        color='Customer_Count',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Conversion rates scatter plot
                if len(dsa_summary) > 1:
                    fig2 = px.scatter(
                        dsa_summary,
                        x='Ticket_Conversion_Rate',
                        y='Scan_Conversion_Rate',
                        size='Customer_Count',
                        hover_name='dsa_mobile',
                        title='Conversion Rates Comparison',
                        labels={
                            'Ticket_Conversion_Rate': 'Ticket Conversion Rate (%)',
                            'Scan_Conversion_Rate': 'Scan Conversion Rate (%)'
                        },
                        color='Customer_Count',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig2, use_container_width=True)

def display_report1_download(report_data):
    """Display download options for Report 1"""
    st.markdown("### 📤 Export Report 1")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Excel Format (Recommended)")
        st.markdown("""
        <div class='info-box'>
            <strong>Complete Report</strong><br>
            All sheets with formatting and calculations
        </div>
        """, unsafe_allow_html=True)
        
        excel_data = create_excel_download(report_data, 'report1')
        st.download_button(
            label="📥 Download Full Excel Report",
            data=excel_data.getvalue(),
            file_name=f"dsa_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_excel_report1"
        )
    
    with col2:
        st.markdown("#### CSV Format")
        st.markdown("""
        <div class='info-box'>
            <strong>Individual Files</strong><br>
            Download specific data sheets
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if 'qualified_customers' in report_data:
                csv1 = report_data['qualified_customers'].to_csv(index=False)
                st.download_button(
                    label="📥 Qualified Customers",
                    data=csv1,
                    file_name="qualified_customers.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with col_b:
            if 'dsa_summary' in report_data:
                csv2 = report_data['dsa_summary'].to_csv(index=False)
                st.download_button(
                    label="📥 DSA Summary",
                    data=csv2,
                    file_name="dsa_summary.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# ================================
# DISPLAY FUNCTIONS FOR REPORT 2
# ================================
def display_report2_metrics(report_data, dsa_filter):
    """Display metrics for Report 2"""
    results_df = report_data.get('report2_results', pd.DataFrame())
    
    # Apply DSA filter
    if dsa_filter and not results_df.empty:
        results_df = filter_by_dsa(results_df, dsa_filter)
    
    # Filter summary rows (those with Customer Count)
    summary_rows = results_df[results_df['Customer Count'] != '']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_dsas = summary_rows['dsa_mobile'].nunique() if not summary_rows.empty else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Active DSAs</div>
            <div class='metric-value'>{format_number(total_dsas)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_customers = summary_rows['Customer Count'].sum() if not summary_rows.empty else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Active Customers</div>
            <div class='metric-value'>{format_number(total_customers)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if not results_df.empty:
            match_count = len(results_df[results_df['match_status'] == 'MATCH'])
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Matched Onboardings</div>
                <div class='metric-value'>{format_number(match_count)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Matched Onboardings</div>
                <div class='metric-value'>0</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        total_payment = summary_rows['Payment'].sum() if not summary_rows.empty else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Commission Due</div>
            <div class='metric-value'>${format_number(total_payment)}</div>
        </div>
        """, unsafe_allow_html=True)

def display_report2_details(report_data, dsa_filter):
    """Display detailed data for Report 2"""
    tab1, tab2, tab3 = st.tabs(["📋 Detailed Analysis", "🎯 Match Analysis", "📊 Performance"])
    
    with tab1:
        results_df = report_data.get('report2_results', pd.DataFrame())
        
        if dsa_filter and not results_df.empty:
            results_df = filter_by_dsa(results_df, dsa_filter)
        
        if not results_df.empty:
            # Add filtering options
            col1, col2 = st.columns(2)
            with col1:
                match_status_options = results_df['match_status'].unique().tolist()
                selected_status = st.multiselect(
                    "Filter by Match Status",
                    options=match_status_options,
                    default=match_status_options
                )
            
            with col2:
                show_summary = st.checkbox("Show Summary Rows Only", value=True)
            
            # Apply filters
            if selected_status:
                results_df = results_df[results_df['match_status'].isin(selected_status)]
            
            if show_summary:
                filtered_df = results_df[results_df['Customer Count'] != '']
            else:
                filtered_df = results_df
            
            st.dataframe(
                filtered_df,
                use_container_width=True,
                height=500,
                column_config={
                    "Payment": st.column_config.NumberColumn("Commission", format="$%.0f"),
                    "match_status": st.column_config.TextColumn(
                        "Match Status",
                        help="MATCH: Customer onboarded by same DSA\nMISMATCH: Customer onboarded by different DSA\nNO ONBOARDING: Customer not onboarded"
                    )
                }
            )
        else:
            st.warning("No detailed analysis data available.")
    
    with tab2:
        results_df = report_data.get('report2_results', pd.DataFrame())
        
        if not results_df.empty:
            # Match status distribution
            if 'match_status' in results_df.columns:
                match_counts = results_df['match_status'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = px.pie(
                        values=match_counts.values,
                        names=match_counts.index,
                        title='Onboarding Match Status Distribution',
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Show match statistics
                    total_customers = len(results_df[results_df['customer_mobile'] != ''])
                    match_rate = (match_counts.get('MATCH', 0) / total_customers * 100) if total_customers > 0 else 0
                    
                    st.metric("Match Rate", f"{match_rate:.1f}%")
                    st.metric("Total Customers", total_customers)
                    st.metric("Matched Customers", match_counts.get('MATCH', 0))
                    st.metric("Mismatched Customers", match_counts.get('MISMATCH', 0))
    
    with tab3:
        results_df = report_data.get('report2_results', pd.DataFrame())
        
        if not results_df.empty:
            # Filter summary rows
            summary_rows = results_df[results_df['Customer Count'] != '']
            
            if not summary_rows.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top DSAs by customer count
                    top10 = summary_rows.sort_values('Customer Count', ascending=False).head(10)
                    fig2 = px.bar(
                        top10,
                        x='dsa_mobile',
                        y='Customer Count',
                        title='Top DSAs by Customer Count',
                        labels={'dsa_mobile': 'DSA Mobile', 'Customer Count': 'Customer Count'},
                        color='Customer Count',
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                with col2:
                    # Payment vs Customer Count
                    fig3 = px.scatter(
                        summary_rows,
                        x='Customer Count',
                        y='Payment',
                        size='Ticket Count',
                        hover_name='dsa_mobile',
                        title='Commission vs Customer Count',
                        labels={'Customer Count': 'Number of Customers', 'Payment': 'Commission ($)'},
                        color='Customer Count',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig3, use_container_width=True)

def display_report2_download(report_data):
    """Display download options for Report 2"""
    st.markdown("### 📤 Export Report 2")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Excel Format")
        st.markdown("""
        <div class='info-box'>
            <strong>Complete Analysis</strong><br>
            All data with formatting
        </div>
        """, unsafe_allow_html=True)
        
        excel_data = create_excel_download(report_data, 'report2')
        st.download_button(
            label="📥 Download Excel Report",
            data=excel_data.getvalue(),
            file_name=f"dsa_detailed_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_excel_report2"
        )
    
    with col2:
        st.markdown("#### CSV Format")
        st.markdown("""
        <div class='info-box'>
            <strong>Detailed Data</strong><br>
            Complete analysis in CSV format
        </div>
        """, unsafe_allow_html=True)
        
        if 'report2_results' in report_data:
            csv_data = report_data['report2_results'].to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Report",
                data=csv_data,
                file_name="dsa_detailed_analysis.csv",
                mime="text/csv",
                use_container_width=True
            )

# ================================
# WELCOME SCREEN
# ================================
def show_welcome_screen():
    """Display welcome screen with instructions"""
    st.markdown("<h1 class='main-header'>DSA Performance Dashboard</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white; margin: 2rem 0;'>
        <h2>🎯 Professional DSA Analytics Platform</h2>
        <p style='font-size: 1.1rem; opacity: 0.9;'>Upload your data files to start analyzing DSA performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='info-box'>
            <h3>📋 How to Use:</h3>
            <ol>
                <li>Upload CSV files in sidebar</li>
                <li>Apply filters if needed</li>
                <li>Select report type</li>
                <li>Click "Process Data"</li>
                <li>View and download reports</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='info-box'>
            <h3>📁 Required Files:</h3>
            <ul>
                <li><strong>Onboarding.csv</strong> - Customer registration data</li>
                <li><strong>Deposit.csv</strong> - Deposit transactions</li>
                <li><strong>Ticket.csv</strong> - Ticket purchases</li>
                <li><strong>ScanToSend.csv</strong> - Scan transactions</li>
                <li><em>Conversion.csv (Optional)</em> - DSA conversion data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Sample data section
    with st.expander("📥 Download Sample Templates", expanded=False):
        st.info("Use these sample templates to understand the required data format.")
        
        # Create sample data
        sample_onboarding = pd.DataFrame({
            'Mobile': ['1234567', '2345678', '3456789'],
            'Customer Referrer Mobile': ['7777777', '7777777', '8888888'],
            'Full Name': ['Customer One', 'Customer Two', 'Customer Three'],
            'Account ID': ['ACC-001', 'ACC-002', 'ACC-003']
        })
        
        sample_deposit = pd.DataFrame({
            'User Identifier': ['1234567', '2345678'],
            'Created By': ['7777777', '7777777'],
            'Amount': [100, 200],
            'Transaction Type': ['CR', 'CR'],
            'Full Name': ['Customer One', 'Customer Two']
        })
        
        col_a, col_b = st.columns(2)
        with col_a:
            csv1 = sample_onboarding.to_csv(index=False)
            st.download_button(
                label="Download Sample Onboarding.csv",
                data=csv1,
                file_name="sample_onboarding.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_b:
            csv2 = sample_deposit.to_csv(index=False)
            st.download_button(
                label="Download Sample Deposit.csv",
                data=csv2,
                file_name="sample_deposit.csv",
                mime="text/csv",
                use_container_width=True
            )

# ================================
# SIDEBAR
# ================================
def render_sidebar():
    """Render sidebar with file uploads and filters"""
    with st.sidebar:
        # Sidebar header with logo
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 class='sidebar-title'>📊 DSA Dashboard</h1>
            <p style='color: white; opacity: 0.8;'>Professional Analytics Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # File Upload Section
        st.markdown("### 📁 Data Upload")
        
        with st.expander("Upload CSV Files", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                onboarding_file = st.file_uploader(
                    "Onboarding CSV",
                    type=['csv'],
                    key="onboarding_upload",
                    help="Customer onboarding data with Mobile and Referrer Mobile columns"
                )
                
                deposit_file = st.file_uploader(
                    "Deposit CSV",
                    type=['csv'],
                    key="deposit_upload",
                    help="Deposit transaction data"
                )
            
            with col2:
                ticket_file = st.file_uploader(
                    "Ticket CSV",
                    type=['csv'],
                    key="ticket_upload",
                    help="Ticket purchase data"
                )
                
                scan_file = st.file_uploader(
                    "Scan CSV",
                    type=['csv'],
                    key="scan_upload",
                    help="Scan-to-send transaction data"
                )
            
            conversion_file = st.file_uploader(
                "Conversion CSV (Optional)",
                type=['csv'],
                key="conversion_upload",
                help="Optional conversion data"
            )
        
        st.markdown("---")
        
        # Filters Section
        st.markdown("### 🔍 Filters")
        
        with st.expander("DSA & Report Filters", expanded=True):
            # DSA Filter
            dsa_filter = st.text_input(
                "DSA Mobile Numbers",
                placeholder="e.g., 1234567, 2345678, 3456789",
                help="Enter multiple DSA numbers separated by commas"
            )
            
            # Report Selection
            report_type = st.radio(
                "Report Type",
                ["📈 Performance Report", "🔍 Detailed Analysis"],
                index=0,
                help="Select the type of analysis to perform"
            )
        
        st.markdown("---")
        
        # Action Buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Clear All", use_container_width=True, help="Clear all data and start fresh"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        with col2:
            process_btn = st.button(
                "🚀 Process Data",
                type="primary",
                use_container_width=True,
                help="Click to process uploaded files and generate reports"
            )
        
        return {
            'files': {
                'onboarding': onboarding_file,
                'deposit': deposit_file,
                'ticket': ticket_file,
                'scan': scan_file,
                'conversion': conversion_file
            },
            'filters': {
                'dsa_filter': dsa_filter,
                'report_type': report_type
            },
            'process_clicked': process_btn
        }

# ================================
# MAIN APPLICATION
# ================================
def main():
    """Main application runner"""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar and get inputs
    sidebar_data = render_sidebar()
    
    # Process files if button clicked
    if sidebar_data['process_clicked']:
        # Store uploaded files in session state
        st.session_state.uploaded_files = sidebar_data['files']
        
        # Validate files
        validation = validate_file(sidebar_data['files'])
        if not validation['valid']:
            st.error(f"❌ {validation['message']}")
        else:
            with st.spinner("🔄 Processing data..."):
                try:
                    analyzer = st.session_state.analyzer
                    
                    # Load and clean data
                    processed_dfs = analyzer.load_and_clean_data(sidebar_data['files'])
                    
                    # Generate selected report
                    report_type = sidebar_data['filters']['report_type']
                    
                    if report_type == "📈 Performance Report":
                        report_data = analyzer.generate_report1(processed_dfs)
                        if report_data:
                            st.session_state.report1_data = report_data
                            st.session_state.report2_data = None
                            st.session_state.current_report = 'report1'
                            st.session_state.processed = True
                            st.success("✅ Report 1 generated successfully!")
                    else:
                        report_data = analyzer.generate_report2(processed_dfs)
                        if report_data:
                            st.session_state.report2_data = report_data
                            st.session_state.report1_data = None
                            st.session_state.current_report = 'report2'
                            st.session_state.processed = True
                            st.success("✅ Report 2 generated successfully!")
                    
                    # Store filters
                    st.session_state.current_filters = sidebar_data['filters']
                    
                except Exception as e:
                    st.error(f"❌ Error processing data: {str(e)}")
    
    # Display results if processed
    if st.session_state.processed:
        if st.session_state.current_report == 'report1' and st.session_state.report1_data:
            # Get current filters
            dsa_filter = ""
            if hasattr(st.session_state, 'current_filters'):
                dsa_filter = st.session_state.current_filters.get('dsa_filter', '')
            
            # Display Report 1
            display_report1_metrics(st.session_state.report1_data, dsa_filter)
            
            # Tabs for Report 1
            tab1, tab2, tab3 = st.tabs(["📋 Data Analysis", "📊 Visualizations", "📥 Export"])
            
            with tab1:
                display_report1_details(st.session_state.report1_data, dsa_filter)
            
            with tab2:
                # Additional visualizations can go here
                dsa_summary = st.session_state.report1_data.get('dsa_summary', pd.DataFrame())
                if not dsa_summary.empty:
                    # Conversion rates over time (if date data available)
                    col1, col2 = st.columns(2)
                    with col1:
                        # Customer distribution by DSA
                        fig = px.pie(
                            dsa_summary,
                            values='Customer_Count',
                            names='dsa_mobile',
                            title='Customer Distribution by DSA',
                            hole=0.3
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Conversion rates bar chart
                        conv_data = dsa_summary.melt(
                            id_vars=['dsa_mobile'],
                            value_vars=['Ticket_Conversion_Rate', 'Scan_Conversion_Rate', 'Deposit_Conversion_Rate'],
                            var_name='Conversion Type',
                            value_name='Rate'
                        )
                        fig = px.bar(
                            conv_data,
                            x='dsa_mobile',
                            y='Rate',
                            color='Conversion Type',
                            barmode='group',
                            title='Conversion Rates by DSA'
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                display_report1_download(st.session_state.report1_data)
        
        elif st.session_state.current_report == 'report2' and st.session_state.report2_data:
            # Get current filters
            dsa_filter = ""
            if hasattr(st.session_state, 'current_filters'):
                dsa_filter = st.session_state.current_filters.get('dsa_filter', '')
            
            # Display Report 2
            display_report2_metrics(st.session_state.report2_data, dsa_filter)
            
            # Tabs for Report 2
            tab1, tab2, tab3 = st.tabs(["📋 Detailed Analysis", "🎯 Insights", "📥 Export"])
            
            with tab1:
                display_report2_details(st.session_state.report2_data, dsa_filter)
            
            with tab2:
                # Show summary statistics
                if 'summary_stats' in st.session_state.report2_data:
                    stats = st.session_state.report2_data['summary_stats']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Overall Statistics")
                        st.metric("Total DSAs", stats['total_dsas'])
                        st.metric("Total Customers", stats['total_customers'])
                        st.metric("Total Commission", f"${format_number(stats['total_payment'])}")
                    
                    with col2:
                        st.markdown("#### Match Status")
                        if stats['match_status_counts']:
                            for status, count in stats['match_status_counts'].items():
                                percentage = (count / stats['total_customers'] * 100) if stats['total_customers'] > 0 else 0
                                st.metric(f"{status}", f"{count} ({percentage:.1f}%)")
                
                # Top DSAs
                if 'summary_stats' in st.session_state.report2_data and st.session_state.report2_data['summary_stats']['top_dsas']:
                    st.markdown("#### Top Performing DSAs")
                    top_dsas_data = pd.DataFrame(st.session_state.report2_data['summary_stats']['top_dsas'])
                    st.dataframe(top_dsas_data, use_container_width=True)
            
            with tab3:
                display_report2_download(st.session_state.report2_data)
    
    else:
        # Show welcome screen
        show_welcome_screen()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6B7280; font-size: 0.9rem;'>"
        "DSA Performance Dashboard v1.0.0 • "
        "<a href='https://github.com/laminkinte/dsa-dashboard' target='_blank'>GitHub</a> • "
        "© 2024 DSA Analytics Team"
        "</div>",
        unsafe_allow_html=True
    )

# ================================
# RUN APPLICATION
# ================================
if __name__ == "__main__":
    main()