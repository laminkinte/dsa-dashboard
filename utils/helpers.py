"""
Helper functions for the DSA dashboard
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import streamlit as st

def format_number(num: int) -> str:
    """Format number with commas"""
    return f"{num:,}"

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
        key=f"download_{filename}"
    )

def calculate_summary_metrics(df: pd.DataFrame) -> Dict:
    """Calculate summary metrics from dataframe"""
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'unique_dsas': df.get('dsa_mobile', pd.Series()).nunique() if 'dsa_mobile' in df.columns else 0,
        'unique_customers': df.get('customer_mobile', pd.Series()).nunique() if 'customer_mobile' in df.columns else 0
    }