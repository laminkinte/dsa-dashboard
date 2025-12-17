"""
Report 1 Analyzer - Complete Implementation
Implements the first DSA performance report logic
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
import warnings

warnings.filterwarnings('ignore')

class Report1Analyzer:
    """Analyzer for Report 1: DSA Performance Report"""
    
    def analyze(self, dfs: Dict) -> Dict:
        """Main analysis function for Report 1"""
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
                raise ValueError("Missing required data files for Report 1")
            
            print("📊 Starting Report 1 Analysis...")
            
            # ================================
            # FIX FULL NAME COLUMN
            # ================================
            name_cols = ["full_name", "Full Name", "Name"]
            name_col = next((c for c in name_cols if c in onboarding.columns), None)
            if name_col is None:
                onboarding["full_name"] = "Unknown"
            else:
                onboarding = onboarding.rename(columns={name_col: "full_name"})

            # ================================
            # RENAME COLUMNS
            # ================================
            onboarding = onboarding.rename(columns={
                "Customer Referrer Mobile": "dsa_mobile",
                "Mobile": "customer_mobile"
            })

            # Deposit customer column
            possible_cols = ['customer_mobile', 'Customer Mobile', 'Mobile', 'User Identifier']
            deposit_customer_col = next((c for c in possible_cols if c in deposit.columns), None)
            if deposit_customer_col is None:
                raise KeyError("No suitable customer/mobile column found in Deposit.csv")
            deposit = deposit.rename(columns={deposit_customer_col: "customer_mobile"})

            if conversion is not None:
                conversion = conversion.rename(columns={"Agent Mobile": "dsa_mobile", "Deposit Count": "deposit_count"})

            # Ticket customer column
            ticket_customer_cols = ["created_by", "user_id", "User Identifier"]
            ticket_customer_col = next((c for c in ticket_customer_cols if c in ticket.columns), None)
            if ticket_customer_col is None:
                raise KeyError(f"No suitable customer column found in Ticket file. Columns: {list(ticket.columns)}")
            ticket = ticket.rename(columns={ticket_customer_col: "customer_mobile", "amount": "ticket_amount"})

            # Scan customer column
            scan_customer_cols = ['Created By', 'Customer Mobile', 'Mobile', 'User Identifier']
            scan_customer_col = next((c for c in scan_customer_cols if c in scan.columns), None)
            if scan_customer_col is None:
                raise KeyError(f"No suitable customer column found in Scan file. Columns: {list(scan.columns)}")
            scan = scan.rename(columns={scan_customer_col: "customer_mobile", "Amount": "scan_amount"})

            # ================================
            # CLEAN DATA
            # ================================
            for df, col in [(onboarding, "customer_mobile"), (onboarding, "dsa_mobile"),
                            (deposit, "customer_mobile"), (ticket, "customer_mobile"),
                            (scan, "customer_mobile")]:
                if df is not None:
                    df[col] = df[col].astype(str).str.strip()

            # Clean numeric columns
            ticket["ticket_amount"] = pd.to_numeric(
                ticket["ticket_amount"].astype(str).str.replace(",", ""), 
                errors='coerce'
            ).fillna(0)
            
            scan["scan_amount"] = pd.to_numeric(
                scan["scan_amount"].astype(str).str.replace(",", ""), 
                errors='coerce'
            ).fillna(0)

            # ================================
            # AGGREGATE TICKET AND SCAN BY CUSTOMER
            # ================================
            # Filter ticket data for customers only
            if "entity_name" in ticket.columns:
                ticket = ticket[ticket["entity_name"].str.lower() == "customer"]
            
            ticket_agg = ticket.groupby("customer_mobile").agg(
                ticket_amount=("ticket_amount", "sum"),
                ticket_count=("ticket_amount", lambda x: (x > 0).sum())
            ).reset_index()
            ticket_agg["bought_ticket"] = (ticket_agg["ticket_amount"] > 0).astype(int)

            scan_summary = scan.groupby("customer_mobile").agg(
                scan_amount=("scan_amount", "sum"),
                scan_count=("scan_amount", "count")
            ).reset_index()
            scan_summary["did_scan"] = (scan_summary["scan_amount"] > 0).astype(int)

            # Get unique depositors
            unique_depositors = deposit[["customer_mobile"]].drop_duplicates().assign(deposited=1)

            # ================================
            # CREATE QUALIFIED CUSTOMERS TABLE (MAIN OUTPUT)
            # ================================
            # Step 1: Get all onboarded customers with their data
            onboarded_customers = onboarding[["dsa_mobile", "customer_mobile", "full_name"]].copy()
            onboarded_customers = onboarded_customers.drop_duplicates(subset=["customer_mobile"])
            
            # Add ticket information
            onboarded_customers = onboarded_customers.merge(
                ticket_agg[["customer_mobile", "bought_ticket", "ticket_amount"]],
                on="customer_mobile", 
                how="left"
            )
            onboarded_customers["bought_ticket"] = onboarded_customers["bought_ticket"].fillna(0).astype(int)
            onboarded_customers["ticket_amount"] = onboarded_customers["ticket_amount"].fillna(0)
            
            # Add scan information
            onboarded_customers = onboarded_customers.merge(
                scan_summary[["customer_mobile", "did_scan", "scan_amount"]],
                on="customer_mobile", 
                how="left"
            )
            onboarded_customers["did_scan"] = onboarded_customers["did_scan"].fillna(0).astype(int)
            onboarded_customers["scan_amount"] = onboarded_customers["scan_amount"].fillna(0)
            
            # Add deposit information
            onboarded_customers = onboarded_customers.merge(
                unique_depositors,
                on="customer_mobile", 
                how="left"
            )
            onboarded_customers["deposited"] = onboarded_customers["deposited"].fillna(0).astype(int)
            
            # Step 2: Filter for QUALIFIED CUSTOMERS only
            # Qualified = Deposited AND (Bought Ticket OR Did Scan)
            qualified_customers = onboarded_customers[
                (onboarded_customers["deposited"] == 1) & 
                ((onboarded_customers["bought_ticket"] == 1) | (onboarded_customers["did_scan"] == 1))
            ].copy()
            
            if qualified_customers.empty:
                print("⚠️ No qualified customers found")
                # Create empty result with correct structure
                qualified_customers_table = pd.DataFrame(columns=[
                    "dsa_mobile", "customer_mobile", "full_name", "bought_ticket", 
                    "did_scan", "deposited", "ticket_amount", "scan_amount",
                    "Customer Count", "Deposit Count", "Ticket Count", 
                    "Scan To Send Count", "Payment (Customer Count *40)",
                    "Payment for customers who were not Onboard by DSA (Should be Empty)"
                ])
            else:
                # Step 3: Group by DSA and add summary columns
                # First, sort by DSA and customer
                qualified_customers = qualified_customers.sort_values(["dsa_mobile", "customer_mobile"])
                
                # Add running counts per DSA
                qualified_customers["Customer Count"] = qualified_customers.groupby("dsa_mobile").cumcount() + 1
                qualified_customers["Deposit Count"] = qualified_customers.groupby("dsa_mobile")["deposited"].cumsum()
                qualified_customers["Ticket Count"] = qualified_customers.groupby("dsa_mobile")["bought_ticket"].cumsum()
                qualified_customers["Scan To Send Count"] = qualified_customers.groupby("dsa_mobile")["did_scan"].cumsum()
                
                # Step 4: Add payment calculations
                qualified_customers["Payment (Customer Count *40)"] = qualified_customers.groupby("dsa_mobile")["Customer Count"].transform(lambda x: x.max() * 40)
                qualified_customers["Payment for customers who were not Onboard by DSA (Should be Empty)"] = ""
                
                # Step 5: Get final max values per DSA for the summary rows
                dsa_summary = qualified_customers.groupby("dsa_mobile").agg(
                    max_customer_count=("Customer Count", "max"),
                    max_deposit_count=("deposited", "sum"),
                    max_ticket_count=("bought_ticket", "sum"),
                    max_scan_count=("did_scan", "sum")
                ).reset_index()
                
                # Step 6: Create the final qualified customers table with summary rows
                qualified_table = []
                
                for dsa in qualified_customers["dsa_mobile"].unique():
                    dsa_customers = qualified_customers[qualified_customers["dsa_mobile"] == dsa]
                    
                    # Add individual customer rows
                    for _, row in dsa_customers.iterrows():
                        qualified_table.append({
                            "dsa_mobile": row["dsa_mobile"],
                            "customer_mobile": row["customer_mobile"],
                            "full_name": row["full_name"],
                            "bought_ticket": row["bought_ticket"],
                            "did_scan": row["did_scan"],
                            "deposited": row["deposited"],
                            "ticket_amount": row["ticket_amount"],
                            "scan_amount": row["scan_amount"],
                            "Customer Count": "",
                            "Deposit Count": "",
                            "Ticket Count": "",
                            "Scan To Send Count": "",
                            "Payment (Customer Count *40)": "",
                            "Payment for customers who were not Onboard by DSA (Should be Empty)": ""
                        })
                    
                    # Add summary row for this DSA
                    summary_row = dsa_summary[dsa_summary["dsa_mobile"] == dsa].iloc[0]
                    qualified_table.append({
                        "dsa_mobile": dsa,
                        "customer_mobile": "",
                        "full_name": "",
                        "bought_ticket": "",
                        "did_scan": "",
                        "deposited": "",
                        "ticket_amount": "",
                        "scan_amount": "",
                        "Customer Count": summary_row["max_customer_count"],
                        "Deposit Count": summary_row["max_deposit_count"],
                        "Ticket Count": summary_row["max_ticket_count"],
                        "Scan To Send Count": summary_row["max_scan_count"],
                        "Payment (Customer Count *40)": summary_row["max_customer_count"] * 40,
                        "Payment for customers who were not Onboard by DSA (Should be Empty)": ""
                    })
                    
                    # Add empty row after each DSA group
                    qualified_table.append({
                        "dsa_mobile": "",
                        "customer_mobile": "",
                        "full_name": "",
                        "bought_ticket": "",
                        "did_scan": "",
                        "deposited": "",
                        "ticket_amount": "",
                        "scan_amount": "",
                        "Customer Count": "",
                        "Deposit Count": "",
                        "Ticket Count": "",
                        "Scan To Send Count": "",
                        "Payment (Customer Count *40)": "",
                        "Payment for customers who were not Onboard by DSA (Should be Empty)": ""
                    })
                
                # Convert to DataFrame
                qualified_customers_table = pd.DataFrame(qualified_table)
            
            # ================================
            # CREATE DSA SUMMARY SHEET
            # ================================
            # Get all onboarded customers (for DSA summary)
            all_onboarded = onboarded_customers.copy()
            
            # DSA Summary - all onboarded customers
            dsa_summary_all = all_onboarded.groupby("dsa_mobile").agg(
                Customer_Count=("customer_mobile", "count"),
                Customers_who_deposited=("deposited", "sum"),
                Customers_who_bought_ticket=("bought_ticket", "sum"),
                Customers_who_did_scan=("did_scan", "sum"),
                Total_Ticket_Amount=("ticket_amount", "sum"),
                Total_Scan_Amount=("scan_amount", "sum")
            ).reset_index()
            
            # Merge with conversion data if available
            if conversion is not None:
                dsa_summary_all = dsa_summary_all.merge(
                    conversion[["dsa_mobile", "deposit_count"]].drop_duplicates(),
                    on="dsa_mobile",
                    how="left"
                )
            
            # Calculate conversion rates
            dsa_summary_all["Ticket_Conversion_Rate"] = (dsa_summary_all["Customers_who_bought_ticket"] / dsa_summary_all["Customer_Count"].replace(0, 1) * 100).round(2)
            dsa_summary_all["Scan_Conversion_Rate"] = (dsa_summary_all["Customers_who_did_scan"] / dsa_summary_all["Customer_Count"].replace(0, 1) * 100).round(2)
            dsa_summary_all["Deposit_Conversion_Rate"] = (dsa_summary_all["Customers_who_deposited"] / dsa_summary_all["Customer_Count"].replace(0, 1) * 100).round(2)
            
            # ================================
            # CREATE ALL CUSTOMERS SHEET
            # ================================
            all_customers = onboarded_customers.copy()
            
            # Add non-onboarded customers who did transactions
            all_transaction_customers = pd.concat([
                ticket_agg["customer_mobile"],
                scan_summary["customer_mobile"],
                unique_depositors["customer_mobile"]
            ]).unique()
            
            onboarded_set = set(onboarding["customer_mobile"])
            non_onboarded_set = set(all_transaction_customers) - onboarded_set
            
            if non_onboarded_set:
                non_onboarded_df = pd.DataFrame({"customer_mobile": list(non_onboarded_set)})
                non_onboarded_df["dsa_mobile"] = "Not Onboarded"
                non_onboarded_df["full_name"] = "Unknown"
                
                # Add ticket info
                non_onboarded_df = non_onboarded_df.merge(
                    ticket_agg[["customer_mobile", "bought_ticket", "ticket_amount"]],
                    on="customer_mobile", 
                    how="left"
                )
                non_onboarded_df["bought_ticket"] = non_onboarded_df["bought_ticket"].fillna(0).astype(int)
                non_onboarded_df["ticket_amount"] = non_onboarded_df["ticket_amount"].fillna(0)
                
                # Add scan info
                non_onboarded_df = non_onboarded_df.merge(
                    scan_summary[["customer_mobile", "did_scan", "scan_amount"]],
                    on="customer_mobile", 
                    how="left"
                )
                non_onboarded_df["did_scan"] = non_onboarded_df["did_scan"].fillna(0).astype(int)
                non_onboarded_df["scan_amount"] = non_onboarded_df["scan_amount"].fillna(0)
                
                # Add deposit info
                non_onboarded_df = non_onboarded_df.merge(
                    unique_depositors,
                    on="customer_mobile", 
                    how="left"
                )
                non_onboarded_df["deposited"] = non_onboarded_df["deposited"].fillna(0).astype(int)
                
                # Combine with onboarded customers
                all_customers = pd.concat([all_customers, non_onboarded_df], ignore_index=True)
            
            print(f"✅ Report 1 Analysis Complete:")
            print(f"   - Total DSA Agents: {len(dsa_summary_all)}")
            print(f"   - Total Onboarded Customers: {len(onboarded_customers)}")
            print(f"   - Total Qualified Customers: {len(qualified_customers) if not qualified_customers.empty else 0}")
            
            # Return all results
            return {
                'qualified_customers': qualified_customers_table,
                'dsa_summary': dsa_summary_all,
                'all_customers': all_customers,
                'ticket_details': ticket,
                'scan_details': scan,
                'deposit_details': deposit,
                'onboarding': onboarding
            }
            
        except Exception as e:
            print(f"❌ Error in Report 1 Analysis: {str(e)}")
            raise

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