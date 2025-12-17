"""
Helper functions for the DSA dashboard
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import streamlit as st
from datetime import datetime
from io import BytesIO

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
    
    return {'valid': True, 'message': 'All files validated successfully'}

def create_excel_download(report_data: Dict, report_type: str = 'report1'):
    """Create Excel download from report data"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if report_type == 'report1':
            if 'qualified_customers' in report_data:
                report_data['qualified_customers'].to_excel(writer, sheet_name='Qualified_Customers', index=False)
            if 'dsa_summary' in report_data:
                report_data['dsa_summary'].to_excel(writer, sheet_name='DSA_Summary', index=False)
        else:
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
