"""
Helper functions for the DSA dashboard
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import streamlit as st
from datetime import datetime

def format_number(num: int) -> str:
    """Format number with commas"""
    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return str(num)

def validate_file(uploaded_files: Dict) -> Dict:
    """Validate uploaded files"""
    required_files = ['onboarding', 'deposit', 'ticket', 'scan']
    
    missing_files = []
    for file_key in required_files:
        if file_key not in uploaded_files or uploaded_files[file_key] is None:
            missing_files.append(file_key)
    
    if missing_files:
        return {
            'valid': False,
            'message': f"Missing required files: {', '.join(missing_files)}"
        }
    
    # Check file extensions
    for file_key, file_obj in uploaded_files.items():
        if file_obj and file_key in required_files:
            if not file_obj.name.lower().endswith('.csv'):
                return {
                    'valid': False,
                    'message': f"{file_key} must be a CSV file"
                }
    
    return {'valid': True, 'message': 'All files validated successfully'}

def create_download_button(data: pd.DataFrame, filename: str, button_text: str = "Download"):
    """Create a styled download button"""
    csv = data.to_csv(index=False)
    
    st.download_button(
        label=button_text,
        data=csv,
        file_name=filename,
        mime="text/csv",
        key=f"download_{datetime.now().timestamp()}"
    )

def calculate_summary_metrics(df: pd.DataFrame) -> Dict:
    """Calculate summary metrics from dataframe"""
    if df.empty:
        return {
            'total_rows': 0,
            'total_columns': 0,
            'missing_values': 0,
            'unique_dsas': 0,
            'unique_customers': 0
        }
    
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'unique_dsas': df.get('dsa_mobile', pd.Series()).nunique() if 'dsa_mobile' in df.columns else 0,
        'unique_customers': df.get('customer_mobile', pd.Series()).nunique() if 'customer_mobile' in df.columns else 0
    }

def create_excel_download(report_data: Dict, report_type: str = 'report1'):
    """Create Excel download from report data"""
    from io import BytesIO
    import pandas as pd
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if report_type == 'report1':
            # Report 1 sheets
            if 'qualified_customers' in report_data:
                report_data['qualified_customers'].to_excel(writer, sheet_name='Qualified_Customers', index=False)
            if 'dsa_summary' in report_data:
                report_data['dsa_summary'].to_excel(writer, sheet_name='DSA_Summary', index=False)
            if 'all_customers' in report_data:
                report_data['all_customers'].to_excel(writer, sheet_name='All_Customers', index=False)
            if 'ticket_details' in report_data:
                report_data['ticket_details'].to_excel(writer, sheet_name='Ticket_Details', index=False)
            if 'scan_details' in report_data:
                report_data['scan_details'].to_excel(writer, sheet_name='Scan_Details', index=False)
            if 'deposit_details' in report_data:
                report_data['deposit_details'].to_excel(writer, sheet_name='Deposit_Details', index=False)
        else:
            # Report 2 sheets
            if 'report2_results' in report_data:
                report_data['report2_results'].to_excel(writer, sheet_name='Detailed_Analysis', index=False)
    
    output.seek(0)
    return output

def filter_by_dsa(data: pd.DataFrame, dsa_filter: str) -> pd.DataFrame:
    """Filter dataframe by DSA mobile numbers"""
    if not dsa_filter or not isinstance(data, pd.DataFrame) or data.empty:
        return data
    
    dsas = [d.strip() for d in dsa_filter.split(',') if d.strip()]
    if not dsas:
        return data
    
    if 'dsa_mobile' in data.columns:
        return data[data['dsa_mobile'].isin(dsas)]
    
    return data

def get_date_columns(df: pd.DataFrame) -> List[str]:
    """Extract date columns from dataframe"""
    date_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(date_term in col_lower for date_term in ['date', 'created', 'updated', 'time', 'at']):
            date_cols.append(col)
    
    return date_cols

def parse_date_column(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Parse date column to datetime"""
    if date_col not in df.columns:
        return df
    
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    except Exception:
        pass
    
    return df