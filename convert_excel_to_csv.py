#!/usr/bin/env python3
"""
Convert all Excel files (.xls, .xlsx) to CSV format
"""

import pandas as pd
import os
from pathlib import Path

data_raw = "data/raw"
excel_files = []

# Find all Excel files
for ext in ['*.xls', '*.xlsx']:
    excel_files.extend(Path(data_raw).glob(ext))

print(f"Found {len(excel_files)} Excel files to convert:\n")

for excel_file in sorted(excel_files):
    print(f"Converting: {excel_file.name}")
    
    # For .xls files, specify xlrd engine
    if excel_file.suffix == '.xls':
        try:
            df = pd.read_excel(excel_file, sheet_name=0)
        except Exception as e:
            print(f"  ⚠️  Error reading {excel_file.name}: {e}")
            print(f"     Trying with different header...")
            try:
                df = pd.read_excel(excel_file, sheet_name=0, header=3)
            except Exception as e2:
                print(f"  ❌ Failed: {e2}")
                continue
    else:
        # For .xlsx files
        try:
            df = pd.read_excel(excel_file, sheet_name=0)
        except Exception as e:
            print(f"  ⚠️  Error reading {excel_file.name}: {e}")
            continue
    
    # Create output filename
    csv_name = excel_file.stem + ".csv"
    csv_path = Path(data_raw) / csv_name
    
    # Save to CSV with semicolon separator
    df.to_csv(csv_path, sep=';', index=False)
    
    print(f"  ✅ Converted to: {csv_name}")
    print(f"     Rows: {len(df):,}, Columns: {len(df.columns)}")
    print(f"     Size: {csv_path.stat().st_size / (1024*1024):.2f} MB\n")

print("=" * 70)
print("✅ Conversion complete!")
print(f"   All Excel files converted to CSV in {data_raw}/")
