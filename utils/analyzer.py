"""
Main DSA Analyzer Module
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

class DSA_Analyzer:
    """Main DSA analysis class"""
    
    def __init__(self):
        self.processed_data = {}
    
    def load_and_clean_data(self, uploaded_files: Dict) -> Optional[Dict]:
        """Load and clean all uploaded files"""
        try:
            dfs = {}
            
            # Read all uploaded files
            for key, file_obj in uploaded_files.items():
                if file_obj is not None:
                    # Reset file pointer to beginning
                    file_obj.seek(0)
                    dfs[key] = pd.read_csv(file_obj, low_memory=False)
            
            return dfs
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None
    
    def clean_mobile_number(self, mobile):
        """Clean mobile numbers to ensure consistency"""
        if pd.isna(mobile):
            return ''
        
        mobile_str = str(mobile)
        # Remove any non-digit characters
        mobile_clean = ''.join(filter(str.isdigit, mobile_str))
        
        # Handle Gambian mobile numbers (7 digits)
        if len(mobile_clean) == 7:
            return mobile_clean
        elif len(mobile_clean) > 7:
            # Take last 7 digits
            return mobile_clean[-7:]
        else:
            return mobile_clean
    
    def generate_report1(self, dfs: Dict) -> Optional[Dict]:
        """Generate Report 1: DSA Performance Analysis"""
        try:
            # Extract dataframes
            onboarding = dfs.get('onboarding')
            deposit = dfs.get('deposit')
            ticket = dfs.get('ticket')
            scan = dfs.get('scan')
            conversion = dfs.get('conversion')
            
            # Validate required data
            if not all([onboarding is not None, deposit is not None,
                       ticket is not None, scan is not None]):
                raise ValueError("Missing required data files")
            
            # Process Report 1 logic here
            # For now, return sample data
            qualified_df = pd.DataFrame({
                'dsa_mobile': ['DSA001', 'DSA002', 'DSA003'],
                'customer_mobile': ['CUST001', 'CUST002', 'CUST003'],
                'full_name': ['Customer One', 'Customer Two', 'Customer Three'],
                'bought_ticket': [1, 0, 1],
                'did_scan': [1, 1, 0],
                'deposited': [1, 1, 1],
                'Customer Count': [1, 1, 1],
                'Deposit Count': [1, 1, 1],
                'Ticket Count': [1, 0, 1],
                'Scan To Send Count': [1, 1, 0],
                'Payment (Customer Count *40)': [40, 40, 40]
            })
            
            dsa_summary = pd.DataFrame({
                'dsa_mobile': ['DSA001', 'DSA002', 'DSA003'],
                'Customer_Count': [10, 15, 8],
                'Customers_who_deposited': [8, 12, 6],
                'Customers_who_bought_ticket': [6, 10, 4],
                'Customers_who_did_scan': [7, 9, 5],
                'Ticket_Conversion_Rate': [60.0, 66.7, 50.0],
                'Scan_Conversion_Rate': [70.0, 60.0, 62.5],
                'Deposit_Conversion_Rate': [80.0, 80.0, 75.0]
            })
            
            return {
                'qualified_customers': qualified_df,
                'dsa_summary': dsa_summary,
                'all_customers': pd.DataFrame(),
                'ticket_details': pd.DataFrame(),
                'scan_details': pd.DataFrame(),
                'deposit_details': pd.DataFrame(),
                'onboarding': pd.DataFrame()
            }
            
        except Exception as e:
            print(f"Error generating Report 1: {str(e)}")
            # Return empty dataframes
            return {
                'qualified_customers': pd.DataFrame(),
                'dsa_summary': pd.DataFrame(),
                'all_customers': pd.DataFrame(),
                'ticket_details': pd.DataFrame(),
                'scan_details': pd.DataFrame(),
                'deposit_details': pd.DataFrame(),
                'onboarding': pd.DataFrame()
            }
    
    def generate_report2(self, dfs: Dict) -> Optional[Dict]:
        """Generate Report 2: Detailed DSA Analysis"""
        try:
            # For now, return sample data
            results_df = pd.DataFrame({
                'dsa_mobile': ['DSA001', 'DSA002', 'DSA003', 'DSA001', 'DSA002'],
                'customer_mobile': ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005'],
                'full_name': ['Customer One', 'Customer Two', 'Customer Three', 'Customer Four', 'Customer Five'],
                'bought_ticket': [1, 0, 1, 1, 0],
                'did_scan': [1, 1, 0, 0, 1],
                'deposited': [1, 1, 1, 1, 1],
                'onboarded_by': ['DSA001', 'DSA002', 'DSA003', 'DSA001', 'DSA002'],
                'match_status': ['MATCH', 'MATCH', 'MATCH', 'MATCH', 'MATCH'],
                'Customer Count': [2, 2, 1, '', ''],
                'Deposit Count': [2, 2, 1, '', ''],
                'Ticket Count': [2, 0, 1, '', ''],
                'Scan To Send Count': [1, 2, 0, '', ''],
                'Payment': [50, 50, 25, '', '']
            })
            
            summary_stats = {
                'total_dsas': 3,
                'total_customers': 5,
                'total_payment': 125,
                'match_status_counts': {'MATCH': 5},
                'top_dsas': [
                    {'dsa_mobile': 'DSA001', 'customer_count': 2, 'payment': 50},
                    {'dsa_mobile': 'DSA002', 'customer_count': 2, 'payment': 50},
                    {'dsa_mobile': 'DSA003', 'customer_count': 1, 'payment': 25}
                ]
            }
            
            return {
                'report2_results': results_df,
                'customer_names': {},
                'onboarding_map': {},
                'summary_stats': summary_stats
            }
            
        except Exception as e:
            print(f"Error generating Report 2: {str(e)}")
            return {
                'report2_results': pd.DataFrame(),
                'customer_names': {},
                'onboarding_map': {},
                'summary_stats': {}
            }
