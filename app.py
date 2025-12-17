"""
DSA Performance Dashboard - Streamlit Cloud Compatible
Simplified version to ensure deployment works
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from io import BytesIO
import sys
import os

# Add utils to path for Streamlit Cloud
sys.path.append(os.path.dirname(__file__))

# Try to import plotly with fallback
PLOTLY_AVAILABLE = False
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    st.sidebar.warning("⚠️ Plotly not installed. Charts disabled.")

# Import custom modules with better error handling
try:
    # First try to import from utils
    from utils.analyzer import DSA_Analyzer
    from utils.helpers import format_number, validate_file
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    st.sidebar.error(f"⚠️ Utils modules not loaded: {str(e)}")
    
    # Create simple fallback analyzer
    class SimpleAnalyzer:
        def __init__(self):
            pass
        
        def load_and_clean_data(self, files):
            """Simple file loader"""
            dfs = {}
            for key, file_obj in files.items():
                if file_obj is not None:
                    try:
                        file_obj.seek(0)
                        dfs[key] = pd.read_csv(file_obj, low_memory=False)
                    except Exception as e:
                        st.error(f"Error reading {key}: {str(e)}")
            return dfs
        
        def generate_report1(self, dfs):
            """Simple Report 1 generator"""
            try:
                # Extract dataframes
                onboarding = dfs.get('onboarding')
                deposit = dfs.get('deposit')
                ticket = dfs.get('ticket')
                scan = dfs.get('scan')
                
                if not all([onboarding is not None, deposit is not None,
                           ticket is not None, scan is not None]):
                    return {
                        'qualified_customers': pd.DataFrame(),
                        'dsa_summary': pd.DataFrame(),
                        'message': 'Missing required files'
                    }
                
                # Simple processing - just return sample structure
                sample_df = pd.DataFrame({
                    'dsa_mobile': ['Sample1', 'Sample2'],
                    'customer_mobile': ['Cust1', 'Cust2'],
                    'full_name': ['Sample Customer 1', 'Sample Customer 2'],
                    'bought_ticket': [1, 0],
                    'did_scan': [1, 1],
                    'deposited': [1, 1]
                })
                
                return {
                    'qualified_customers': sample_df,
                    'dsa_summary': pd.DataFrame({'dsa_mobile': ['Sample1'], 'Customer_Count': [2]}),
                    'message': 'Sample data - upload real files for analysis'
                }
                
            except Exception as e:
                return {
                    'qualified_customers': pd.DataFrame(),
                    'dsa_summary': pd.DataFrame(),
                    'message': f'Error: {str(e)}'
                }
        
        def generate_report2(self, dfs):
            """Simple Report 2 generator"""
            sample_df = pd.DataFrame({
                'dsa_mobile': ['Sample1', 'Sample2'],
                'customer_mobile': ['Cust1', 'Cust2'],
                'full_name': ['Sample Customer 1', 'Sample Customer 2'],
                'bought_ticket': [1, 0],
                'did_scan': [1, 1],
                'deposited': [1, 1],
                'onboarded_by': ['Sample1', 'Sample2'],
                'match_status': ['MATCH', 'MATCH']
            })
            
            return {
                'report2_results': sample_df,
                'message': 'Sample data - upload real files for detailed analysis'
            }
    
    # Create fallback functions
    def format_number(num):
        try:
            return f"{int(num):,}"
        except:
            return str(num)
    
    def validate_file(uploaded_files):
        required_files = ['onboarding', 'deposit', 'ticket', 'scan']
        missing_files = []
        for file_key in required_files:
            if file_key not in uploaded_files or uploaded_files[file_key] is None:
                missing_files.append(file_key)
        
        if missing_files:
            return {'valid': False, 'message': f"Missing required files: {', '.join(missing_files)}"}
        return {'valid': True, 'message': 'All files validated'}

warnings.filterwarnings('ignore')

# ================================
# PAGE CONFIGURATION
# ================================
st.set_page_config(
    page_title="DSA Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# CUSTOM CSS
# ================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        text-transform: uppercase;
    }
    .info-box {
        background: #dbeafe;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #3B82F6;
    }
    .success-box {
        background: #d1fae5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #10B981;
    }
    .warning-box {
        background: #fef3c7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #F59E0B;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# SESSION STATE
# ================================
if 'analyzer' not in st.session_state:
    if MODULES_AVAILABLE:
        st.session_state.analyzer = DSA_Analyzer()
    else:
        st.session_state.analyzer = SimpleAnalyzer()

if 'report1_data' not in st.session_state:
    st.session_state.report1_data = None
if 'report2_data' not in st.session_state:
    st.session_state.report2_data = None
if 'processed' not in st.session_state:
    st.session_state.processed = False

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.title("📊 DSA Dashboard")
    st.markdown("---")
    
    st.subheader("📁 Upload Data")
    
    onboarding_file = st.file_uploader("Onboarding CSV", type=['csv'], key="onboarding")
    deposit_file = st.file_uploader("Deposit CSV", type=['csv'], key="deposit")
    ticket_file = st.file_uploader("Ticket CSV", type=['csv'], key="ticket")
    scan_file = st.file_uploader("Scan CSV", type=['csv'], key="scan")
    conversion_file = st.file_uploader("Conversion CSV (Optional)", type=['csv'], key="conversion")
    
    st.markdown("---")
    
    st.subheader("🔍 Filters")
    
    dsa_filter = st.text_input(
        "DSA Mobile Numbers",
        placeholder="e.g., 1234567, 2345678",
        help="Enter multiple DSA numbers separated by commas"
    )
    
    report_type = st.radio(
        "Report Type",
        ["📈 Performance Report", "🔍 Detailed Analysis"],
        index=0
    )
    
    st.markdown("---")
    
    if st.button("🚀 Process Data", type="primary", use_container_width=True):
        st.session_state.process_clicked = True
    else:
        st.session_state.process_clicked = False

# ================================
# MAIN CONTENT
# ================================
st.markdown("<h1 class='main-header'>DSA Performance Dashboard</h1>", unsafe_allow_html=True)

if st.session_state.process_clicked:
    uploaded_files = {
        'onboarding': onboarding_file,
        'deposit': deposit_file,
        'ticket': ticket_file,
        'scan': scan_file,
        'conversion': conversion_file
    }
    
    # Validate files
    validation = validate_file(uploaded_files)
    if not validation['valid']:
        st.error(f"❌ {validation['message']}")
    else:
        with st.spinner("🔄 Processing data..."):
            try:
                analyzer = st.session_state.analyzer
                
                # Load data
                processed_dfs = analyzer.load_and_clean_data(uploaded_files)
                
                # Generate report
                if report_type == "📈 Performance Report":
                    report_data = analyzer.generate_report1(processed_dfs)
                    if report_data:
                        st.session_state.report1_data = report_data
                        st.session_state.report2_data = None
                        st.session_state.processed = True
                        st.success("✅ Report 1 generated successfully!")
                else:
                    report_data = analyzer.generate_report2(processed_dfs)
                    if report_data:
                        st.session_state.report2_data = report_data
                        st.session_state.report1_data = None
                        st.session_state.processed = True
                        st.success("✅ Report 2 generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing data: {str(e)}")

# Display results
if st.session_state.processed:
    if st.session_state.report1_data:
        report_data = st.session_state.report1_data
        
        # Display metrics
        st.markdown("### 📊 Performance Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'dsa_summary' in report_data and not report_data['dsa_summary'].empty:
                total_dsas = report_data['dsa_summary']['dsa_mobile'].nunique()
            else:
                total_dsas = 0
            st.metric("Total DSAs", total_dsas)
        
        with col2:
            if 'qualified_customers' in report_data and not report_data['qualified_customers'].empty:
                total_customers = len(report_data['qualified_customers'])
            else:
                total_customers = 0
            st.metric("Total Customers", total_customers)
        
        with col3:
            if 'message' in report_data:
                st.info(f"ℹ️ {report_data['message']}")
        
        # Display data
        st.markdown("### 📋 Data")
        if 'qualified_customers' in report_data and not report_data['qualified_customers'].empty:
            st.dataframe(report_data['qualified_customers'], use_container_width=True)
        
        # Download option
        st.markdown("### 📥 Download")
        if 'qualified_customers' in report_data and not report_data['qualified_customers'].empty:
            csv = report_data['qualified_customers'].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="dsa_report.csv",
                mime="text/csv"
            )
    
    elif st.session_state.report2_data:
        report_data = st.session_state.report2_data
        
        st.markdown("### 🔍 Detailed Analysis")
        
        if 'report2_results' in report_data and not report_data['report2_results'].empty:
            st.dataframe(report_data['report2_results'], use_container_width=True)
            
            # Download option
            st.markdown("### 📥 Download")
            csv = report_data['report2_results'].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="dsa_detailed_analysis.csv",
                mime="text/csv"
            )
        
        if 'message' in report_data:
            st.info(f"ℹ️ {report_data['message']}")

else:
    # Welcome screen
    st.markdown("""
    <div class='info-box'>
        <h3>Welcome to DSA Performance Dashboard</h3>
        <p>Upload your CSV files to analyze DSA performance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📋 How to Use:**
        1. Upload CSV files in sidebar
        2. Apply filters if needed
        3. Select report type
        4. Click "Process Data"
        5. View and download reports
        """)
    
    with col2:
        st.markdown("""
        **📁 Required Files:**
        - Onboarding.csv
        - Deposit.csv  
        - Ticket.csv
        - ScanToSend.csv
        - (Optional) Conversion.csv
        """)
    
    # Sample data
    with st.expander("📥 Need Sample Templates?"):
        sample_df = pd.DataFrame({
            'Mobile': ['1234567', '2345678'],
            'Customer Referrer Mobile': ['7777777', '7777777'],
            'Full Name': ['Sample Customer 1', 'Sample Customer 2']
        })
        
        csv = sample_df.to_csv(index=False)
        st.download_button(
            label="Download Sample Onboarding.csv",
            data=csv,
            file_name="sample_onboarding.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("DSA Performance Dashboard v1.0 • Streamlit Cloud")
