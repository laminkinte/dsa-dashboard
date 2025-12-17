"""
Report 2 Analyzer - Complete Implementation
Implements the second detailed analysis report logic
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

class Report2Analyzer:
    """Analyzer for Report 2: Detailed DSA Analysis"""
    
    def analyze(self, dfs: Dict) -> Dict:
        """Main analysis function for Report 2"""
        try:
            # Extract dataframes
            onboarding = dfs.get('onboarding')
            deposit = dfs.get('deposit')
            ticket = dfs.get('ticket')
            scan = dfs.get('scan')
            
            # Validate required data
            if not all([onboarding is not None, deposit is not None,
                       ticket is not None, scan is not None]):
                raise ValueError("Missing required data files for Report 2")
            
            print("🔍 Starting Report 2 Analysis...")
            
            # ================================
            # PREPROCESS DATA
            # ================================
            onboarding, deposit, ticket, scan = self.preprocess_data(
                onboarding, deposit, ticket, scan
            )
            
            # ================================
            # GET CUSTOMER NAMES AND ONBOARDING MAPPING
            # ================================
            customer_names, onboarding_map = self.get_customer_names_and_onboarding(
                onboarding, deposit, ticket, scan
            )
            
            print(f"✓ Collected {len(customer_names):,} customer names")
            print(f"✓ Found {len(onboarding_map):,} onboarding records")
            
            # ================================
            # ANALYZE TRANSACTIONS
            # ================================
            dsa_customers = self.analyze_transactions(
                deposit, ticket, scan, customer_names, onboarding_map
            )
            
            if not dsa_customers:
                print("⚠️ No DSA-customer transactions found")
                # Create empty result with correct structure
                results_df = pd.DataFrame(columns=[
                    'dsa_mobile', 'customer_mobile', 'full_name', 'bought_ticket', 
                    'did_scan', 'deposited', 'onboarded_by', 'match_status',
                    'Customer Count', 'Deposit Count', 'Ticket Count', 
                    'Scan To Send Count', 'Payment'
                ])
            else:
                # ================================
                # CREATE FORMATTED OUTPUT
                # ================================
                results_df = self.create_formatted_output(dsa_customers)
            
            print(f"✅ Report 2 Analysis Complete: {len(results_df):,} rows generated")
            
            # Generate summary statistics
            summary_stats = self.generate_summary_statistics(results_df)
            
            # Return all results
            return {
                'report2_results': results_df,
                'customer_names': customer_names,
                'onboarding_map': onboarding_map,
                'summary_stats': summary_stats
            }
            
        except Exception as e:
            print(f"❌ Error in Report 2 Analysis: {str(e)}")
            raise
    
    def preprocess_data(self, onboarding_df, deposit_df, ticket_df, scan_df):
        """Preprocess and clean all dataframes"""
        # Clean column names
        for df in [onboarding_df, deposit_df, ticket_df, scan_df]:
            df.columns = df.columns.str.strip()
        
        # Clean mobile numbers in all dataframes
        print("Cleaning mobile numbers...")
        
        # Onboarding data
        if 'Mobile' in onboarding_df.columns:
            onboarding_df['Mobile'] = onboarding_df['Mobile'].apply(self.clean_mobile_number)
        if 'Customer Referrer Mobile' in onboarding_df.columns:
            onboarding_df['Customer Referrer Mobile'] = onboarding_df['Customer Referrer Mobile'].apply(self.clean_mobile_number)
        
        # Deposit data
        if 'User Identifier' in deposit_df.columns:
            deposit_df['User Identifier'] = deposit_df['User Identifier'].apply(self.clean_mobile_number)
        if 'Created By' in deposit_df.columns:
            deposit_df['Created By'] = deposit_df['Created By'].apply(self.clean_mobile_number)
        
        # Ticket data
        if 'User Identifier' in ticket_df.columns:
            ticket_df['User Identifier'] = ticket_df['User Identifier'].apply(self.clean_mobile_number)
        if 'Created By' in ticket_df.columns:
            ticket_df['Created By'] = ticket_df['Created By'].apply(self.clean_mobile_number)
        
        # Scan data
        if 'User Identifier' in scan_df.columns:
            scan_df['User Identifier'] = scan_df['User Identifier'].apply(self.clean_mobile_number)
        if 'Created By' in scan_df.columns:
            scan_df['Created By'] = scan_df['Created By'].apply(self.clean_mobile_number)
        
        return onboarding_df, deposit_df, ticket_df, scan_df
    
    def clean_mobile_number(self, mobile):
        """Clean mobile numbers to ensure consistency"""
        if pd.isna(mobile):
            return None
        
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
    
    def get_customer_names_and_onboarding(self, onboarding_df, deposit_df, ticket_df, scan_df):
        """Get customer names from all sources and create onboarding mapping"""
        customer_names = {}
        onboarding_map = {}
        
        # Priority 1: Onboarding data (most reliable)
        if 'Mobile' in onboarding_df.columns and 'Full Name' in onboarding_df.columns:
            for _, row in onboarding_df.dropna(subset=['Mobile']).iterrows():
                mobile = row['Mobile']
                name = row.get('Full Name')
                if mobile and name and pd.notna(name):
                    customer_names[mobile] = str(name).strip()
                
                # Also get onboarding mapping
                referrer = row.get('Customer Referrer Mobile')
                if mobile and referrer and pd.notna(referrer):
                    onboarding_map[mobile] = referrer
        
        # Priority 2: Deposit data
        if 'User Identifier' in deposit_df.columns and 'Full Name' in deposit_df.columns:
            for _, row in deposit_df.dropna(subset=['User Identifier']).iterrows():
                mobile = row['User Identifier']
                name = row.get('Full Name')
                if mobile and name and pd.notna(name) and mobile not in customer_names:
                    customer_names[mobile] = str(name).strip()
        
        # Priority 3: Ticket data
        if 'User Identifier' in ticket_df.columns and 'Full Name' in ticket_df.columns:
            for _, row in ticket_df.dropna(subset=['User Identifier']).iterrows():
                mobile = row['User Identifier']
                name = row.get('Full Name')
                if mobile and name and pd.notna(name) and mobile not in customer_names:
                    customer_names[mobile] = str(name).strip()
        
        # Priority 4: Scan data
        if 'User Identifier' in scan_df.columns and 'Full Name' in scan_df.columns:
            for _, row in scan_df.dropna(subset=['User Identifier']).iterrows():
                mobile = row['User Identifier']
                name = row.get('Full Name')
                if mobile and name and pd.notna(name) and mobile not in customer_names:
                    customer_names[mobile] = str(name).strip()
        
        return customer_names, onboarding_map
    
    def analyze_transactions(self, deposit_df, ticket_df, scan_df, customer_names, onboarding_map):
        """Analyze all transactions and group by DSA"""
        # Group customers by DSA who handled their deposits
        dsa_customers = {}
        
        # 1. Analyze deposits (CR = Credit to customer)
        customer_deposits = deposit_df[deposit_df['Transaction Type'] == 'CR'].copy()
        
        for _, row in customer_deposits.iterrows():
            customer_mobile = row['User Identifier']
            dsa_mobile = row['Created By']
            
            # Skip if same number or invalid
            if not customer_mobile or not dsa_mobile or customer_mobile == dsa_mobile:
                continue
            
            # Initialize DSA entry if not exists
            if dsa_mobile not in dsa_customers:
                dsa_customers[dsa_mobile] = {}
            
            # Initialize customer entry if not exists
            if customer_mobile not in dsa_customers[dsa_mobile]:
                dsa_customers[dsa_mobile][customer_mobile] = {
                    'full_name': customer_names.get(customer_mobile, 'Unknown'),
                    'deposit_count': 0,
                    'bought_ticket': 0,
                    'did_scan': 0,
                    'onboarded_by': onboarding_map.get(customer_mobile, 'NOT ONBOARDED'),
                    'match_status': 'NO ONBOARDING' if customer_mobile not in onboarding_map else 'MISMATCH'
                }
            
            # Update deposit count
            dsa_customers[dsa_mobile][customer_mobile]['deposit_count'] += 1
        
        # 2. Analyze ticket purchases (DR = Debit from customer)
        customer_tickets = ticket_df[ticket_df['Transaction Type'] == 'DR'].copy()
        
        for _, row in customer_tickets.iterrows():
            customer_mobile = row['User Identifier']
            if not customer_mobile:
                continue
            
            # Check if this customer deposited with any DSA
            for dsa_mobile, customers in dsa_customers.items():
                if customer_mobile in customers:
                    customers[customer_mobile]['bought_ticket'] += 1
                    break
        
        # 3. Analyze scan transactions (DR = Debit from customer)
        customer_scans = scan_df[scan_df['Transaction Type'] == 'DR'].copy()
        
        for _, row in customer_scans.iterrows():
            customer_mobile = row['User Identifier']
            if not customer_mobile:
                continue
            
            # Check if this customer deposited with any DSA
            for dsa_mobile, customers in dsa_customers.items():
                if customer_mobile in customers:
                    customers[customer_mobile]['did_scan'] += 1
                    break
        
        # 4. Update match status for onboarded customers
        for dsa_mobile, customers in dsa_customers.items():
            for customer_mobile, customer_data in customers.items():
                onboarded_by = customer_data['onboarded_by']
                if onboarded_by != 'NOT ONBOARDED':
                    customer_data['match_status'] = 'MATCH' if onboarded_by == dsa_mobile else 'MISMATCH'
        
        print(f"✓ Found {len(dsa_customers):,} DSAs with customer transactions")
        
        # Count customers with ticket/scan activity
        active_customers = 0
        for dsa_mobile, customers in dsa_customers.items():
            for customer_mobile, customer_data in customers.items():
                if customer_data['bought_ticket'] > 0 or customer_data['did_scan'] > 0:
                    active_customers += 1
        
        print(f"✓ {active_customers:,} customers have ticket or scan activity")
        
        return dsa_customers
    
    def create_formatted_output(self, dsa_customers):
        """Create output in the exact format requested"""
        # Create a list to hold all rows
        all_rows = []
        
        for dsa_mobile, customers in dsa_customers.items():
            # Calculate summary for this DSA
            active_customers = []
            for customer_mobile, customer_data in customers.items():
                if customer_data['bought_ticket'] > 0 or customer_data['did_scan'] > 0:
                    active_customers.append(customer_mobile)
            
            if not active_customers:
                continue  # Skip DSA if no active customers
            
            customer_count = len(active_customers)
            deposit_count = sum(customers[c]['deposit_count'] for c in active_customers)
            ticket_count = sum(customers[c]['bought_ticket'] for c in active_customers)
            scan_count = sum(customers[c]['did_scan'] for c in active_customers)
            payment = customer_count * 25  # $25 per qualified customer
            
            # Add summary row (first customer row with summary columns filled)
            first_customer = active_customers[0]
            first_customer_data = customers[first_customer]
            
            summary_row = {
                'dsa_mobile': dsa_mobile,
                'customer_mobile': first_customer,
                'full_name': first_customer_data['full_name'],
                'bought_ticket': first_customer_data['bought_ticket'],
                'did_scan': first_customer_data['did_scan'],
                'deposited': first_customer_data['deposit_count'],
                'onboarded_by': first_customer_data['onboarded_by'],
                'match_status': first_customer_data['match_status'],
                'Customer Count': customer_count,
                'Deposit Count': deposit_count,
                'Ticket Count': ticket_count,
                'Scan To Send Count': scan_count,
                'Payment': payment
            }
            all_rows.append(summary_row)
            
            # Add remaining customer rows (with empty summary columns)
            for i, customer_mobile in enumerate(active_customers[1:], 1):
                customer_data = customers[customer_mobile]
                
                customer_row = {
                    'dsa_mobile': dsa_mobile,
                    'customer_mobile': customer_mobile,
                    'full_name': customer_data['full_name'],
                    'bought_ticket': customer_data['bought_ticket'],
                    'did_scan': customer_data['did_scan'],
                    'deposited': customer_data['deposit_count'],
                    'onboarded_by': customer_data['onboarded_by'],
                    'match_status': customer_data['match_status'],
                    'Customer Count': '',
                    'Deposit Count': '',
                    'Ticket Count': '',
                    'Scan To Send Count': '',
                    'Payment': ''
                }
                all_rows.append(customer_row)
        
        # Create DataFrame
        results_df = pd.DataFrame(all_rows)
        
        # Define column order exactly as requested
        columns = [
            'dsa_mobile', 'customer_mobile', 'full_name', 'bought_ticket', 
            'did_scan', 'deposited', 'onboarded_by', 'match_status',
            'Customer Count', 'Deposit Count', 'Ticket Count', 
            'Scan To Send Count', 'Payment'
        ]
        
        results_df = results_df[columns]
        
        return results_df
    
    def generate_summary_statistics(self, results_df):
        """Generate summary statistics for Report 2"""
        if results_df.empty:
            return {
                'total_dsas': 0,
                'total_customers': 0,
                'total_payment': 0,
                'match_status_counts': {},
                'top_dsas': []
            }
        
        # Filter rows that have Customer Count (summary rows)
        summary_rows = results_df[results_df['Customer Count'] != '']
        
        total_dsas = summary_rows['dsa_mobile'].nunique()
        total_customers = summary_rows['Customer Count'].sum() if not summary_rows.empty else 0
        total_payment = summary_rows['Payment'].sum() if not summary_rows.empty else 0
        
        # Analyze match status
        all_customer_rows = results_df[results_df['customer_mobile'] != '']
        match_status_counts = dict(all_customer_rows['match_status'].value_counts())
        
        # Top DSAs by customer count
        top_dsas = []
        if not summary_rows.empty:
            top_dsas_data = summary_rows.sort_values('Customer Count', ascending=False).head(5)
            for _, row in top_dsas_data.iterrows():
                top_dsas.append({
                    'dsa_mobile': row['dsa_mobile'],
                    'customer_count': int(row['Customer Count']),
                    'payment': int(row['Payment'])
                })
        
        return {
            'total_dsas': total_dsas,
            'total_customers': total_customers,
            'total_payment': total_payment,
            'match_status_counts': match_status_counts,
            'top_dsas': top_dsas
        }