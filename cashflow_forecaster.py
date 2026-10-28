#!/usr/bin/env python3
"""
MSME AI Cashflow Forecaster
Starter script for Indian MSMEs.

Demonstrates basic cash-flow forecasting using sample invoice data
with GST awareness and working capital estimation.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_msme_data():
    """Generate realistic sample invoice data for an Indian MSME."""
    np.random.seed(42)
    base_date = datetime(2026, 10, 28)
    
    data = {
        'invoice_id': [f'INV-{1000+i}' for i in range(15)],
        'customer': ['Retail Chain A', 'Wholesaler B', 'Online Seller C', 'Govt Vendor D'] * 4 + ['Local Shop'],
        'invoice_date': [base_date - timedelta(days=np.random.randint(1, 60)) for _ in range(15)],
        'due_date': [base_date + timedelta(days=np.random.randint(15, 45)) for _ in range(15)],
        'amount': np.random.randint(25000, 250000, 15),  # INR
        'gst_rate': np.random.choice([0.05, 0.12, 0.18], 15),
        'status': np.random.choice(['pending', 'partial', 'paid'], 15, p=[0.5, 0.2, 0.3])
    }
    df = pd.DataFrame(data)
    df['gst_amount'] = (df['amount'] * df['gst_rate']).round(0)
    df['total_with_gst'] = df['amount'] + df['gst_amount']
    return df

def forecast_cashflow(df, days_ahead=90, starting_balance=150000):
    """
    Simple heuristic cash-flow forecast.
    - Pending invoices expected to pay on due date (with some delay risk)
    - Outflows for GST payments and operating costs
    """
    today = datetime(2026, 10, 28)
    dates = [today + timedelta(days=i) for i in range(days_ahead)]
    cash_positions = []
    balance = starting_balance
    
    # Simple operating outflow assumption (monthly ~40k INR)
    daily_opex = 40000 / 30
    
    for day in dates:
        # Inflows: invoices due today (assume 70% collection rate for pending)
        due_today = df[(df['due_date'].dt.date == day.date()) & (df['status'] != 'paid')]
        inflow = due_today['total_with_gst'].sum() * 0.70
        
        # Outflows
        outflow = daily_opex
        # GST payment window (simplified: 20th of month)
        if day.day == 20:
            outflow += df['gst_amount'].sum() * 0.3  # partial GST liability
        
        balance += inflow - outflow
        cash_positions.append({
            'date': day.strftime('%Y-%m-%d'),
            'inflow': round(inflow, 0),
            'outflow': round(outflow, 0),
            'balance': round(balance, 0)
        })
    
    return pd.DataFrame(cash_positions)

def estimate_working_capital(forecast_df, buffer_days=45):
    """Estimate recommended working capital based on lowest projected balance."""
    min_balance = forecast_df['balance'].min()
    avg_daily_outflow = forecast_df['outflow'].mean()
    recommended = max(0, -min_balance) + (avg_daily_outflow * buffer_days)
    return round(recommended, 0)

def main():
    print("=== MSME AI Cashflow Forecaster (Demo) ===\n")
    print("Generating sample Indian MSME invoice data...\n")
    
    df = generate_sample_msme_data()
    print("Sample Invoices (first 5):")
    print(df[['invoice_id', 'customer', 'amount', 'gst_amount', 'due_date', 'status']].head().to_string(index=False))
    print()
    
    forecast = forecast_cashflow(df)
    print("30-day Cash Flow Snapshot (every 5 days):")
    print(forecast.iloc[::5][['date', 'inflow', 'outflow', 'balance']].head(6).to_string(index=False))
    print()
    
    wc = estimate_working_capital(forecast)
    min_bal = forecast['balance'].min()
    print(f"Lowest projected balance (next 90 days): ₹{min_bal:,.0f}")
    print(f"Recommended working capital buffer: ₹{wc:,.0f}")
    print()
    
    if min_bal < 50000:
        print("⚠️  Alert: Potential cash shortfall detected. Consider accelerating collections or arranging short-term credit.")
    else:
        print("✅ Cash position looks healthy in the near term.")
    
    print("\n--- Demo complete. Extend this script with real data or ML models. ---")

if __name__ == "__main__":
    main()
